#!/usr/bin/env python3
"""
build_presentation_video.py - Generates synchronized Full HD presentation videos.
Implements the continuous master audio architecture and constant frame rate (CFR) still image filter.
Part of the english-class-slides (v1.2) skill package.
"""

import os
import sys
import time
import json
import subprocess
import argparse
from pathlib import Path
from PIL import Image
import numpy as np
import imageio_ffmpeg
import soundfile as sf

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def check_nvenc(ffmpeg_exe):
    try:
        res = subprocess.run([ffmpeg_exe, "-hide_banner", "-encoders"], capture_output=True, text=True)
        if "h264_nvenc" in res.stdout:
            test = subprocess.run(
                [ffmpeg_exe, "-y", "-f", "lavfi", "-i", "nullsrc=s=1920x1080:d=0.1", "-c:v", "h264_nvenc", "-f", "null", "-"],
                capture_output=True
            )
            return test.returncode == 0
    except Exception:
        pass
    return False

def export_frames_from_pptx(pptx_path, out_frames_dir, width=1920, height=1080):
    print(f"\n[PPTX EXPORT] Exporting {pptx_path.name} to {out_frames_dir.name} ({width}x{height})...")
    out_frames_dir.mkdir(parents=True, exist_ok=True)
    try:
        import win32com.client
        ppt_app = win32com.client.Dispatch("PowerPoint.Application")
        abs_pptx = str(pptx_path.resolve())
        pres = ppt_app.Presentations.Open(abs_pptx, WithWindow=False)
        count = pres.Slides.Count
        for i in range(1, count + 1):
            out_png = out_frames_dir / f"slide_{i:02d}.png"
            pres.Slides(i).Export(str(out_png.resolve()), "PNG", width, height)
        pres.Close()
        ppt_app.Quit()
        print(f"[OK] Exported {count} slide frames successfully.")
    except Exception as e:
        print(f"[!] Warning: PowerPoint COM export failed ({e}). Checking existing frames.")

def build_video_continuous(config, lang="ja", audio_dir=None, out_mp4=None, force_export=False):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    has_nvenc = check_nvenc(ffmpeg_exe)
    video_codec = "h264_nvenc" if has_nvenc else "libx264"

    topic = config.get("topic", "presentation")
    paths = config.get("paths", {})
    pptx_path = Path(paths.get(f"output_pptx_{lang}", f"output/slides_{topic}_{lang}.pptx")).resolve()
    frames_dir = Path(paths.get("output_frames_dir", f"output/frames_{topic}_{lang}")).resolve()

    if audio_dir:
        a_dir = Path(audio_dir).resolve()
    else:
        a_dir = Path(paths.get(f"audio_dir_{lang}", f"Audio/{lang.capitalize()}")).resolve()

    if not frames_dir.exists() or len(list(frames_dir.glob("slide_*.png"))) == 0 or force_export:
        if pptx_path.exists():
            export_frames_from_pptx(pptx_path, frames_dir)
        else:
            raise FileNotFoundError(f"Neither frames nor PPTX found: {pptx_path}")

    frames = sorted(list(frames_dir.glob("slide_*.png")))
    total_slides = len(frames)
    print(f"Total Slide Frames: {total_slides} in {frames_dir.name}")

    # Inspect Audio Tracks
    audio_files = []
    durations = []
    sr = 24000
    for i in range(1, total_slides + 1):
        # check wav first, then mp3
        w = a_dir / f"slide_{i:02d}.wav"
        if not w.exists():
            w = a_dir / f"slide_{i:02d}_raw.wav"
        if not w.exists():
            w = a_dir / f"slide_{i:02d}.mp3"
        if not w.exists():
            w = a_dir / f"slide_{i:02d}_control.wav"
        if not w.exists():
            raise FileNotFoundError(f"Audio track missing for slide {i:02d} in {a_dir}")
        audio_files.append(w)
        d, cur_sr = sf.read(str(w))
        durations.append(len(d) / cur_sr)
        sr = cur_sr

    # Build Master Continuous PCM Track
    print(f"\n[MASTER AUDIO] Assembling continuous audio stream for {total_slides} slides...")
    inter_gap_s = 0.50
    post_gap_s = 0.50
    inter_gap_samples = int(sr * inter_gap_s)
    post_gap_samples = int(sr * post_gap_s)

    master_pcm_parts = []
    timeline_entries = []

    for i in range(total_slides):
        s_num = i + 1
        d_data, _ = sf.read(str(audio_files[i]))
        if d_data.ndim > 1: d_data = d_data[:, 0]
        dur = durations[i]

        if i == 0:
            v_start = 0.0
            a_start = 0.0
            a_end = dur
            v_end = dur + (inter_gap_s / 2.0)
        elif i < total_slides - 1:
            v_start = timeline_entries[-1]["visual_end"]
            a_start = timeline_entries[-1]["audio_end"] + inter_gap_s
            a_end = a_start + dur
            v_end = a_end + (inter_gap_s / 2.0)
        else: # last slide
            v_start = timeline_entries[-1]["visual_end"]
            a_start = timeline_entries[-1]["audio_end"] + inter_gap_s
            a_end = a_start + dur
            v_end = a_end + post_gap_s

        v_dur = v_end - v_start
        timeline_entries.append({
            "slide": s_num,
            "visual_start": v_start,
            "visual_end": v_end,
            "visual_dur": v_dur,
            "audio_start": a_start,
            "audio_end": a_end,
            "audio_dur": dur
        })
        master_pcm_parts.append(d_data)
        if i < total_slides - 1:
            master_pcm_parts.append(np.zeros(inter_gap_samples))
        else:
            master_pcm_parts.append(np.zeros(post_gap_samples))

    master_pcm = np.concatenate(master_pcm_parts)
    master_wav_path = Path(paths.get("master_audio_wav", f"output/{topic}_{lang}_master.wav")).resolve()
    master_wav_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(master_wav_path), master_pcm, sr, subtype='PCM_16')
    print(f"[OK] Master audio track created: {master_wav_path.name} ({len(master_pcm)/sr:.2f}s)")

    # Write Concat List
    concat_txt_path = master_wav_path.parent / f"video_{topic}_{lang}_concat.txt"
    c_lines = []
    for entry in timeline_entries:
        s_num = entry["slide"]
        fp = (frames_dir / f"slide_{s_num:02d}.png").resolve().as_posix()
        c_lines.append(f"file '{fp}'")
        c_lines.append(f"duration {entry['visual_dur']:.4f}")
    # Repeat last frame
    last_fp = (frames_dir / f"slide_{total_slides:02d}.png").resolve().as_posix()
    c_lines.append(f"file '{last_fp}'")
    concat_txt_path.write_text("\n".join(c_lines), encoding="utf-8")

    # Render MP4 Video in One Single Continuous Pass
    final_mp4 = Path(out_mp4 or paths.get("output_video_mp4", f"output/{topic}_{lang}_presentation.mp4")).resolve()
    final_mp4.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n[FFmpeg RENDER] Rendering 1080p CFR video ({video_codec})...")
    cmd = [
        ffmpeg_exe, "-y",
        "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt_path),
        "-i", str(master_wav_path),
        "-vf", "fps=30,format=yuv420p",
        "-c:v", video_codec,
    ]
    if video_codec == "h264_nvenc":
        cmd.extend(["-preset", "p4", "-cq", "20"])
    else:
        cmd.extend(["-preset", "medium", "-crf", "18", "-tune", "stillimage"])

    cmd.extend([
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(final_mp4)
    ])

    t0 = time.time()
    subprocess.run(cmd, check=True)
    elapsed = time.time() - t0

    sz_mb = final_mp4.stat().st_size / (1024 * 1024)
    total_dur = len(master_pcm) / sr
    print("\n" + "=" * 65)
    print(f"★ PRESENTATION VIDEO BUILT SUCCESSFULLY!")
    print(f"  Output Video: {final_mp4} ({sz_mb:.2f} MB)")
    print(f"  Duration    : {total_dur/60:.0f}:{total_dur%60:02.0f} ({total_dur:.2f}s)")
    print(f"  Resolution  : 1920x1080 Full HD (16:9, constant 30 fps)")
    print(f"  Render Time : {elapsed:.1f} seconds")
    print("=" * 65)
    return final_mp4

def main():
    parser = argparse.ArgumentParser(description="Assemble synchronized 1080p presentation video.")
    parser.add_argument("--config", default="pkg_v1.2/english-class-slides/examples/summer_vacation_japan/deck_config.json", help="Path to deck_config.json")
    parser.add_argument("--lang", default="ja", choices=["ja", "en", "es"], help="Target language (default: ja)")
    parser.add_argument("--audio-dir", default=None, help="Custom audio directory")
    parser.add_argument("--output", default=None, help="Custom output video path")
    parser.add_argument("--force-export", action="store_true", help="Force re-exporting slide frames from PPTX")
    args = parser.parse_args()

    cfg_p = Path(args.config)
    if not cfg_p.exists():
        cfg_p = Path("deck_config.json")
    config = json.loads(cfg_p.read_text(encoding="utf-8"))

    build_video_continuous(config, lang=args.lang, audio_dir=args.audio_dir, out_mp4=args.output, force_export=args.force_export)

if __name__ == "__main__":
    main()

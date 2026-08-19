#!/usr/bin/env python3
"""
build_presentation_video.py - Generates synchronized Full HD presentation videos (v1.3).
Universal video builder supporting English, Spanish, and Japanese with continuous master audio architecture.
Part of the english-class-slides (v1.3) skill package.
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

def find_audio_file(a_dir, slide_num):
    candidates = [
        f"{slide_num:02d}.mp3",
        f"{slide_num:02d}.wav",
        f"slide_{slide_num:02d}.mp3",
        f"slide_{slide_num:02d}.wav",
        f"slide_{slide_num:02d}_raw.wav",
        f"slide_{slide_num:02d}_control.wav",
        f"Tracks/{slide_num:02d}.mp3",
        f"Tracks/{slide_num:02d}.wav",
        f"Tracks/slide_{slide_num:02d}.mp3",
        f"Tracks/slide_{slide_num:02d}.wav"
    ]
    for c in candidates:
        p = a_dir / c
        if p.exists() and p.stat().st_size > 0:
            return p
    return None

def build_video_continuous(config, lang="ja", audio_dir=None, out_mp4=None, frames_dir_override=None, force_export=False):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    has_nvenc = check_nvenc(ffmpeg_exe)
    video_codec = "h264_nvenc" if has_nvenc else "libx264"

    topic = config.get("topic", "presentation")
    paths = config.get("paths", {})
    pptx_path = Path(paths.get(f"output_pptx_{lang}", f"output/slides_{topic}_{lang}.pptx")).resolve()
    
    if frames_dir_override:
        frames_dir = Path(frames_dir_override).resolve()
    elif Path(f"renders/{lang}").exists() and len(list(Path(f"renders/{lang}").glob("slide_*.png"))) > 0:
        frames_dir = Path(f"renders/{lang}").resolve()
    else:
        frames_dir = Path(paths.get("output_frames_dir", f"output/frames_{topic}_{lang}")).resolve()

    if audio_dir:
        a_dir = Path(audio_dir).resolve()
    else:
        # Default audio dir check
        default_dir = Path(paths.get(f"audio_dir_{lang}", f"Audio/{lang.capitalize()}")).resolve()
        if (default_dir / "Tracks").exists():
            a_dir = (default_dir / "Tracks").resolve()
        else:
            a_dir = default_dir

    if not frames_dir.exists() or len(list(frames_dir.glob("slide_*.png"))) == 0 or force_export:
        if pptx_path.exists():
            export_frames_from_pptx(pptx_path, frames_dir)
        else:
            raise FileNotFoundError(f"Neither frames nor PPTX found: {pptx_path}")

    frames = sorted(list(frames_dir.glob("slide_*.png")))
    total_slides = len(frames)
    print(f"\n[ASSETS] Total Slide Frames: {total_slides} in {frames_dir.name}")
    print(f"[ASSETS] Audio Source Directory: {a_dir}")

    # Inspect Audio Tracks
    audio_files = []
    raw_audios = []
    durations = []
    target_sr = 44100

    for i in range(1, total_slides + 1):
        af = find_audio_file(a_dir, i)
        if not af:
            raise FileNotFoundError(f"Audio track missing for slide {i:02d} in {a_dir}")
        audio_files.append(af)
        data, cur_sr = sf.read(str(af))
        if data.ndim == 1:
            data = np.column_stack([data, data])
        elif data.ndim == 2 and data.shape[1] == 1:
            data = np.column_stack([data[:, 0], data[:, 0]])
        raw_audios.append(data)
        dur = len(data) / cur_sr
        durations.append(dur)
        target_sr = cur_sr

    print(f"[OK] Found and validated {total_slides} audio tracks.")

    # Build Master Continuous PCM Track & Timeline
    print(f"\n[MASTER AUDIO] Assembling continuous audio stream for {total_slides} slides ({lang.upper()})...")
    inter_gap_s = 0.500
    post_gap_s = 0.500
    inter_gap_samples = int(target_sr * inter_gap_s)
    post_gap_samples = int(target_sr * post_gap_s)

    master_pcm_parts = []
    timeline_entries = []

    for i in range(total_slides):
        s_num = i + 1
        d_data = raw_audios[i]
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
            master_pcm_parts.append(np.zeros((inter_gap_samples, 2)))
        else:
            master_pcm_parts.append(np.zeros((post_gap_samples, 2)))

    master_pcm = np.concatenate(master_pcm_parts, axis=0)
    master_wav_path = Path(paths.get("master_audio_wav", f"output/summer_vacation_{lang}_master_continuous.wav")).resolve()
    master_wav_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(master_wav_path), master_pcm, target_sr, subtype='PCM_16')
    print(f"[OK] Master audio track created: {master_wav_path.name} ({len(master_pcm)/target_sr:.2f}s)")

    # Write Timeline and Chapters
    timeline_txt_path = master_wav_path.parent / f"summer_vacation_presentation_{lang}_timeline.txt"
    chapters_txt_path = master_wav_path.parent / f"summer_vacation_presentation_{lang}_chapters.txt"
    
    t_lines = ["SLIDE | VISUAL START | AUDIO START | AUDIO END | VISUAL END | DURATION"]
    t_lines.append("-" * 75)
    c_lines = []

    for entry in timeline_entries:
        s = entry["slide"]
        v_s = entry["visual_start"]
        a_s = entry["audio_start"]
        a_e = entry["audio_end"]
        v_e = entry["visual_end"]
        v_d = entry["visual_dur"]
        
        mins = int(v_s // 60)
        secs = int(v_s % 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        t_lines.append(f" {s:02d}   |   {v_s:7.3f}s   |  {a_s:7.3f}s  |  {a_e:7.3f}s |  {v_e:7.3f}s  | {v_d:6.3f}s")
        c_lines.append(f"{time_str} Slide {s:02d}")

    timeline_txt_path.write_text("\n".join(t_lines), encoding="utf-8")
    chapters_txt_path.write_text("\n".join(c_lines), encoding="utf-8")
    print(f"[OK] Timeline saved: {timeline_txt_path.name}")
    print(f"[OK] Chapters saved: {chapters_txt_path.name}")

    # Write Concat List
    concat_txt_path = master_wav_path.parent / f"video_{lang}_img_concat.txt"
    c_lines_concat = []
    for entry in timeline_entries:
        s_num = entry["slide"]
        fp = (frames_dir / f"slide_{s_num:02d}.png").resolve().as_posix()
        c_lines_concat.append(f"file '{fp}'")
        c_lines_concat.append(f"duration {entry['visual_dur']:.4f}")
    # Repeat last frame without duration for FFmpeg demuxer
    last_fp = (frames_dir / f"slide_{total_slides:02d}.png").resolve().as_posix()
    c_lines_concat.append(f"file '{last_fp}'")
    concat_txt_path.write_text("\n".join(c_lines_concat), encoding="utf-8")

    # Render MP4 Video in One Single Continuous Pass
    final_mp4 = Path(out_mp4 or paths.get("output_video_mp4", f"output/summer_vacation_presentation_{lang}.mp4")).resolve()
    final_mp4.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n[FFmpeg RENDER] Rendering 1080p CFR video ({video_codec})...")
    cmd = [
        ffmpeg_exe, "-y",
        "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt_path),
        "-i", str(master_wav_path),
        "-map", "0:v", "-map", "1:a",
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
    total_dur = len(master_pcm) / target_sr
    print("\n" + "=" * 65)
    print(f"★ PRESENTATION VIDEO BUILT SUCCESSFULLY ({lang.upper()})!")
    print(f"  Output Video: {final_mp4} ({sz_mb:.2f} MB)")
    print(f"  Duration    : {total_dur/60:.0f}:{total_dur%60:02.0f} ({total_dur:.2f}s)")
    print(f"  Resolution  : 1920x1080 Full HD (16:9, constant 30 fps CFR)")
    print(f"  Render Time : {elapsed:.1f} seconds")
    print("=" * 65)
    return final_mp4

def main():
    parser = argparse.ArgumentParser(description="Assemble synchronized 1080p presentation video.")
    parser.add_argument("--config", default="deck_config.json", help="Path to deck_config.json")
    parser.add_argument("--lang", default="en", choices=["ja", "en", "es"], help="Target language (default: en)")
    parser.add_argument("--audio-dir", default=None, help="Custom audio directory")
    parser.add_argument("--frames-dir", default=None, help="Custom frames directory")
    parser.add_argument("--output", default=None, help="Custom output video path")
    parser.add_argument("--force-export", action="store_true", help="Force re-exporting slide frames from PPTX")
    args = parser.parse_args()

    cfg_p = Path(args.config)
    if not cfg_p.exists():
        cfg_p = Path("pkg_v1.2/english-class-slides/examples/summer_vacation_japan/deck_config.json")
    if not cfg_p.exists():
        cfg_p = Path(".agents/skills/english-class-slides/examples/summer_vacation_japan/deck_config.json")
    config = json.loads(cfg_p.read_text(encoding="utf-8"))

    build_video_continuous(config, lang=args.lang, audio_dir=args.audio_dir, frames_dir_override=args.frames_dir, out_mp4=args.output, force_export=args.force_export)

if __name__ == "__main__":
    main()

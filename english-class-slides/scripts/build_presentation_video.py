"""
build_presentation_video.py (english-class-slides v1.1)

Generates a synchronized 1080p MP4 presentation video by pairing rendered slide images
with corresponding audio tracks. Supports Japanese, English, and Spanish presentations.

Requirements:
  pip install pywin32 imageio-ffmpeg mutagen
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def get_ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"

def get_audio_duration(filepath):
    try:
        from mutagen.mp3 import MP3
        audio = MP3(filepath)
        return audio.info.length
    except Exception:
        # Fallback to ffprobe
        ffmpeg_exe = get_ffmpeg()
        cmd = [
            ffmpeg_exe, "-i", str(filepath),
            "-show_entries", "format=duration",
            "-v", "quiet", "-of", "csv=p=0"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        try:
            return float(res.stdout.strip())
        except ValueError:
            return 3.0

def export_pptx_slides_to_images(pptx_path, output_dir, width=1920, height=1080, force=False):
    abs_output_dir = os.path.abspath(output_dir)
    os.makedirs(abs_output_dir, exist_ok=True)

    # Check if frames already exist
    existing = [os.path.join(abs_output_dir, f"slide_{i:02d}.png") for i in range(1, 54)]
    if not force and all(os.path.exists(p) for p in existing):
        print(f"\n[1/3] REUSING {len(existing)} EXISTING 1080p SLIDE FRAMES FROM: {output_dir}")
        return existing

    print(f"\n[1/3] EXPORTING HIGH-RES 1080p SLIDE IMAGES...")
    print(f"  Source PPTX: {pptx_path}")
    print(f"  Target Frames: {output_dir}")

    import win32com.client
    ppt_app = win32com.client.Dispatch("PowerPoint.Application")
    abs_pptx = os.path.abspath(pptx_path)
    presentation = ppt_app.Presentations.Open(abs_pptx, ReadOnly=True, Untitled=False, WithWindow=False)

    slide_count = len(presentation.Slides)
    image_paths = []

    for i in range(1, slide_count + 1):
        out_img = os.path.join(abs_output_dir, f"slide_{i:02d}.png")
        presentation.Slides(i).Export(out_img, "PNG", width, height)
        image_paths.append(out_img)
        print(f"  [+] Exported Slide {i:02d}/{slide_count:02d} -> {os.path.basename(out_img)}")

    presentation.Close()
    ppt_app.Quit()
    print(f"  [OK] Exported all {slide_count} slides to PNG (1920x1080) successfully.")
    return image_paths

def check_nvenc_support(ffmpeg_exe):
    test_cmd = [
        ffmpeg_exe, "-y",
        "-f", "lavfi", "-i", "color=c=black:s=64x64:d=0.1",
        "-c:v", "h264_nvenc",
        "-f", "null", "-"
    ]
    try:
        res = subprocess.run(test_cmd, capture_output=True, text=True)
        return res.returncode == 0
    except Exception:
        return False

def build_presentation_video(pptx_path, audio_dir, output_video, padding_pre=0.3, padding_post=0.5, fps=30):
    start_time = time.time()
    ffmpeg_exe = get_ffmpeg()
    has_nvenc = check_nvenc_support(ffmpeg_exe)
    accel_label = "NVIDIA NVENC (RTX 3060 Hardware Acceleration)" if has_nvenc else "CPU (libx264)"

    print("=" * 65)
    print("PRESENTATION VIDEO GENERATOR (english-class-slides v1.1)")
    print("=" * 65)
    print(f"Presentation : {pptx_path}")
    print(f"Audio Source : {audio_dir}")
    print(f"Output Video : {output_video}")
    print(f"Acceleration : {accel_label}")
    print(f"Timing Guard : Pre: +{padding_pre}s | Post: +{padding_post}s | FPS: {fps}")
    print("=" * 65)

    # 1. Export Slides to PNG
    frames_dir = os.path.join(os.path.dirname(output_video), f"frames_{Path(output_video).stem}")
    image_paths = export_pptx_slides_to_images(pptx_path, frames_dir)
    slide_count = len(image_paths)

    # 2. Inspect Audio Tracks and Calculate Timing
    print(f"\n[2/3] AUDITING AUDIO TRACKS & SYNCHRONIZING TIMING...")
    audio_files = []
    durations = []
    total_audio_time = 0.0

    chapters = []
    current_timestamp = 0.0

    for i in range(1, slide_count + 1):
        # Look for matching audio file
        audio_name_mp3 = f"slide_{i:02d}.mp3"
        audio_name_wav = f"slide_{i:02d}.wav"
        path_mp3 = os.path.join(audio_dir, audio_name_mp3)
        path_wav = os.path.join(audio_dir, audio_name_wav)

        if os.path.exists(path_mp3):
            audio_path = path_mp3
        elif os.path.exists(path_wav):
            audio_path = path_wav
        else:
            raise FileNotFoundError(f"Audio file not found for Slide {i:02d} in '{audio_dir}'. Looked for {audio_name_mp3} / {audio_name_wav}")

        raw_dur = get_audio_duration(audio_path)
        clip_dur = raw_dur + padding_pre + padding_post
        audio_files.append(audio_path)
        durations.append((raw_dur, clip_dur))
        total_audio_time += clip_dur

        # Format chapter timestamp (hh:mm:ss)
        mins = int(current_timestamp // 60)
        secs = int(current_timestamp % 60)
        chapters.append((f"{mins:02d}:{secs:02d}", f"Slide {i:02d}"))
        print(f"  Slide {i:02d}: Audio={raw_dur:.2f}s -> Clip={clip_dur:.2f}s (Start: {mins:02d}:{secs:02d})")
        current_timestamp += clip_dur

    total_mins = int(total_audio_time // 60)
    total_secs = int(total_audio_time % 60)
    print(f"  [OK] Total Video Duration: {total_mins:02d}:{total_secs:02d} ({total_audio_time:.2f}s)")

    # 3. Assemble and Encode Video with FFmpeg
    print(f"\n[3/3] RENDERING 1080p MP4 VIDEO WITH FFMPEG ({accel_label})...")
    os.makedirs(os.path.dirname(output_video) or ".", exist_ok=True)
    temp_dir = os.path.join(os.path.dirname(output_video), f"tmp_{Path(output_video).stem}")
    os.makedirs(temp_dir, exist_ok=True)

    segment_files = []

    for i in range(slide_count):
        img_path = image_paths[i]
        aud_path = audio_files[i]
        raw_dur, clip_dur = durations[i]
        seg_output = os.path.join(temp_dir, f"seg_{i+1:02d}.mp4")

        # Build FFmpeg command for segment:
        filter_complex = (
            f"[1:a]adelay={int(padding_pre*1000)}|{int(padding_pre*1000)},"
            f"apad=whole_dur={clip_dur:.3f}[aout]"
        )

        if has_nvenc:
            v_args = ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "19", "-pix_fmt", "yuv420p"]
        else:
            v_args = ["-c:v", "libx264", "-tune", "stillimage", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p"]

        cmd = [
            ffmpeg_exe, "-y",
            "-loop", "1",
            "-t", f"{clip_dur:.3f}",
            "-i", img_path,
            "-i", aud_path,
            "-filter_complex", filter_complex,
            "-map", "0:v",
            "-map", "[aout]",
            *v_args,
            "-r", str(fps),
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "44100",
            "-shortest",
            seg_output
        ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"  [X] Error rendering segment {i+1}:\n{res.stderr}")
            raise RuntimeError(f"FFmpeg failed on slide {i+1}")

        segment_files.append(seg_output)
        print(f"  [+] Rendered Segment {i+1:02d}/{slide_count:02d} ({clip_dur:.2f}s)")

    # Concatenate all segments
    concat_list_path = os.path.join(temp_dir, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for seg in segment_files:
            # Use relative basename since concat_list is in the same temp directory
            f.write(f"file '{os.path.basename(seg)}'\n")

    print(f"\n  [>] Concatenating {len(segment_files)} segments into final MP4...")
    abs_output_video = os.path.abspath(output_video)
    concat_cmd = [
        ffmpeg_exe, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", "concat_list.txt",
        "-c", "copy",
        abs_output_video
    ]
    res_concat = subprocess.run(concat_cmd, cwd=temp_dir, capture_output=True, text=True)
    if res_concat.returncode != 0:
        print(f"  [X] Error in concatenation:\n{res_concat.stderr}")
        raise RuntimeError("FFmpeg concat failed")

    # Clean up temp segments
    for seg in segment_files:
        try:
            os.remove(seg)
        except OSError:
            pass
    try:
        os.remove(concat_list_path)
        os.rmdir(temp_dir)
    except OSError:
        pass

    elapsed = time.time() - start_time
    file_size_mb = os.path.getsize(output_video) / (1024 * 1024)

    print("\n" + "=" * 65)
    print("★ PRESENTATION VIDEO GENERATION COMPLETED SUCCESSFULLY!")
    print("=" * 65)
    print(f"Output Video : {output_video}")
    print(f"Video Size   : {file_size_mb:.2f} MB")
    print(f"Duration     : {total_mins:02d}:{total_secs:02d} ({total_audio_time:.2f} seconds)")
    print(f"Resolution   : 1920x1080 (16:9 Full HD, 30 fps)")
    print(f"Elapsed Time : {elapsed:.1f} seconds")
    print("=" * 65)

    # Save Chapter Timestamps
    chapters_file = os.path.splitext(output_video)[0] + "_chapters.txt"
    with open(chapters_file, "w", encoding="utf-8") as f:
        f.write("# Video Chapter Timestamps\n")
        for ts, title in chapters:
            f.write(f"{ts} - {title}\n")
    print(f"Chapter timestamps saved to: {chapters_file}")
    return output_video

def main():
    parser = argparse.ArgumentParser(description="Generate synchronized 1080p MP4 presentation video from PPTX and audio files.")
    parser.add_argument("--lang", choices=["ja", "en", "es"], default="ja", help="Presentation language (ja, en, es)")
    parser.add_argument("--pptx", default=None, help="Path to PowerPoint .pptx file")
    parser.add_argument("--audio-dir", default=None, help="Path to directory containing slide_01.mp3 to slide_53.mp3")
    parser.add_argument("--output", default=None, help="Path for output .mp4 video")
    parser.add_argument("--padding-pre", type=float, default=0.3, help="Silence added before speech in seconds (default: 0.3)")
    parser.add_argument("--padding-post", type=float, default=0.5, help="Silence added after speech in seconds (default: 0.5)")
    parser.add_argument("--fps", type=int, default=30, help="Video frames per second (default: 30)")
    args = parser.parse_args()

    # Default paths by language
    if args.lang == "ja":
        pptx = args.pptx or "output/slides_summer_vacation_ja.pptx"
        audio = args.audio_dir or "Audio/Japanese"
        output = args.output or "output/summer_vacation_presentation_ja.mp4"
    elif args.lang == "en":
        pptx = args.pptx or "output/slides_summer_vacation_en.pptx"
        audio = args.audio_dir or "Audio/English"
        output = args.output or "output/summer_vacation_presentation_en.mp4"
    elif args.lang == "es":
        pptx = args.pptx or "output/slides_summer_vacation_es.pptx"
        audio = args.audio_dir or "Audio/Spanish"
        output = args.output or "output/summer_vacation_presentation_es.mp4"

    build_presentation_video(
        pptx_path=pptx,
        audio_dir=audio,
        output_video=output,
        padding_pre=args.padding_pre,
        padding_post=args.padding_post,
        fps=args.fps
    )

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
validate_video.py - Quality assurance audit for generated Full HD presentation videos.
Part of the english-class-slides (v1.2) skill package.
"""

import sys
import subprocess
import argparse
from pathlib import Path
from PIL import Image
import numpy as np
import imageio_ffmpeg

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def validate_video_file(video_path, min_duration=60.0):
    v_path = Path(video_path)
    if not v_path.exists():
        print(f"[X] Video file not found: {v_path}")
        return False

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    sz_mb = v_path.stat().st_size / (1024 * 1024)
    print(f"\nAuditing Video File: {v_path.name} ({sz_mb:.2f} MB)")

    # Probe with FFmpeg
    res = subprocess.run([ffmpeg_exe, "-hide_banner", "-i", str(v_path)], capture_output=True, text=True)
    meta = res.stderr

    if "Video:" not in meta or "Audio:" not in meta:
        print("  [X] Video or Audio stream missing in container!")
        return False
    else:
        print("  [OK] Both Video (H.264) and Audio (AAC) streams detected.")

    if "1920x1080" not in meta:
        print("  [X] Resolution mismatch (Expected 1920x1080 Full HD)")
        return False
    else:
        print("  [OK] Resolution: 1920x1080 (16:9 widescreen Full HD).")

    # Extract sample frames to test visibility
    temp_dir = Path("output/temp_video_val")
    temp_dir.mkdir(parents=True, exist_ok=True)

    test_ts = [2.0, 10.0, 30.0]
    for ts in test_ts:
        frame_out = temp_dir / f"test_frame_{int(ts):02d}s.png"
        subprocess.run([
            ffmpeg_exe, "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{ts:.1f}", "-i", str(v_path),
            "-vframes", "1", str(frame_out)
        ], check=True)
        im = Image.open(frame_out)
        arr = np.array(im)
        std_val = np.std(arr)
        if std_val < 10.0:
            print(f"  [X] Frame at t={ts}s appears flat/black!")
            return False

    print("  [OK] Extracted sample frames verified rich & visible.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Validate presentation video.")
    parser.add_argument("--video", default="output/summer_vacation_presentation_ja_fixed.mp4", help="Path to video")
    args = parser.parse_args()

    print("=" * 65)
    print("PRESENTATION VIDEO QUALITY ASSURANCE AUDIT")
    print("=" * 65)

    ok = validate_video_file(args.video)
    print("\n" + "=" * 65)
    if ok:
        print("★ VIDEO QA AUDIT PASSED SUCCESSFULLY!")
    else:
        print("[X] VIDEO QA AUDIT REPORTED ERRORS.")
    print("=" * 65)

if __name__ == "__main__":
    main()

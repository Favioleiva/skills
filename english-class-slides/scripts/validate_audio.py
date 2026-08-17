#!/usr/bin/env python3
"""
validate_audio.py - Quality assurance audit for synthesized/imported presentation audio files.
Part of the english-class-slides (v1.2) skill package.
"""

import sys
import argparse
from pathlib import Path

def validate_audio_folder(folder_path, expected_count=53):
    f_dir = Path(folder_path)
    if not f_dir.exists():
        print(f"[X] Directory not found: {f_dir}")
        return False

    files = sorted(list(f_dir.glob("slide_*.mp3")) + list(f_dir.glob("slide_*.wav")))
    print(f"\nAuditing Folder: {f_dir.resolve()}")
    print(f"Found Audio Files: {len(files)}/{expected_count}")

    if len(files) != expected_count:
        print(f"  [X] Audio count mismatch: Got {len(files)}, expected {expected_count}")
        return False

    empty_files = [f.name for f in files if f.stat().st_size == 0]
    if empty_files:
        print(f"  [X] Empty audio files detected: {empty_files}")
        return False

    total_size_mb = sum(f.stat().st_size for f in files) / (1024 * 1024)
    print(f"  [OK] All {expected_count} audio files verified non-empty ({total_size_mb:.2f} MB total).")
    return True

def main():
    parser = argparse.ArgumentParser(description="Validate audio assets.")
    parser.add_argument("--audio-dir", default="Audio/Japanese", help="Path to audio directory")
    parser.add_argument("--expected-count", type=int, default=53, help="Expected slide audio count")
    args = parser.parse_args()

    print("=" * 65)
    print("AUDIO ASSETS QUALITY ASSURANCE AUDIT")
    print("=" * 65)

    ok = validate_audio_folder(args.audio_dir, args.expected_count)
    print("\n" + "=" * 65)
    if ok:
        print("★ AUDIO QA AUDIT PASSED SUCCESSFULLY!")
    else:
        print("[X] AUDIO QA AUDIT REPORTED ISSUES.")
    print("=" * 65)

if __name__ == "__main__":
    main()

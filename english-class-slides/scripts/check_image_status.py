#!/usr/bin/env python3
"""
check_image_status.py - Check generated slide image backgrounds.
Part of the english-class-slides (v1.2) skill package.
"""

import os
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Check image assets completion status.")
    parser.add_argument("--images-dir", default="output/images", help="Path to images folder")
    parser.add_argument("--total-designs", type=int, default=14, help="Total designs expected (e.g. 14)")
    args = parser.parse_args()

    img_dir = Path(args.images_dir)
    print("=" * 65)
    print("SLIDE BACKGROUND IMAGES ASSET AUDIT")
    print("=" * 65)
    print(f"Directory: {img_dir.resolve()}\n")

    if not img_dir.exists():
        print(f"[!] Directory not found: {img_dir}")
        sys.exit(1)

    completed = []
    missing = []

    for d in range(args.total_designs):
        d_str = f"design_{d:02d}"
        matches = list(img_dir.glob(f"{d_str}*.png")) + list(img_dir.glob(f"{d_str}*.jpg"))
        if matches:
            sz = matches[0].stat().st_size / 1024
            completed.append((d_str, matches[0].name, sz))
        else:
            missing.append(d_str)

    print(f"Completed Designs: {len(completed)}/{args.total_designs}")
    for d_tag, name, sz in completed:
        print(f"  [+] {d_tag}: {name} ({sz:.1f} KB)")

    if missing:
        print(f"\nMissing Designs ({len(missing)}):")
        for m in missing:
            print(f"  [X] {m}")
    else:
        print(f"\n★ ALL {args.total_designs} IMAGE DESIGNS ARE READY!")
    print("=" * 65)

if __name__ == "__main__":
    main()

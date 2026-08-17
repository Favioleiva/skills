import os
import sys
import argparse

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Check image generation status for slide backgrounds.")
    parser.add_argument("--images-dir", default="output/images", help="Path to directory containing background images")
    parser.add_argument("--total-designs", type=int, default=14, help="Total number of designs (00 to D+1, default: 14)")
    return parser.parse_args()

def check_images(images_dir, total_designs):
    print("=" * 60)
    print(f"IMAGE ASSET STATUS CHECKER (english-class-slides v1.1)")
    print(f"Directory: {os.path.abspath(images_dir)}")
    print("=" * 60)

    if not os.path.exists(images_dir):
        print(f"\n[!] Directory does not exist: {images_dir}")
        print("Status: 0 images found.")
        print(f"Resume Action: Start generation from Design 00 (Cover).")
        return

    expected_files = []
    # Design 00 (Cover)
    expected_files.append((0, "design_00_cover.png"))
    # Designs 01 to total_designs-1
    for d in range(1, total_designs):
        expected_files.append((d, f"design_{d:02d}.png"))

    completed = []
    missing = []

    for d_idx, fname in expected_files:
        fpath = os.path.join(images_dir, fname)
        if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
            size_kb = round(os.path.getsize(fpath) / 1024, 1)
            completed.append((d_idx, fname, size_kb))
        else:
            missing.append((d_idx, fname))

    print(f"\n[+] Completed Designs ({len(completed)}/{total_designs}):")
    for d_idx, fname, size_kb in completed:
        print(f"  [OK] Design {d_idx:02d}: {fname} ({size_kb} KB)")

    if missing:
        print(f"\n[-] Missing / Incomplete Designs ({len(missing)}/{total_designs}):")
        for d_idx, fname in missing:
            print(f"  [MISSING] Design {d_idx:02d}: {fname}")
        first_missing = missing[0][0]
        print(f"\n[>] QUOTA RESUME INSTRUCTION:")
        print(f"  • Do NOT regenerate completed designs (00 to {completed[-1][0]:02d}).")
        print(f"  • Resume image generation directly from Design {first_missing:02d} ({missing[0][1]}).")
    else:
        print("\n[ALL COMPLETE] ALL EXPECTED BACKGROUND DESIGNS ARE READY FOR ASSEMBLY!")

if __name__ == "__main__":
    args = parse_args()
    check_images(args.images_dir, args.total_designs)

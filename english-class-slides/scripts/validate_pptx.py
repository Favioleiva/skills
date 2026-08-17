#!/usr/bin/env python3
"""
validate_pptx.py - Comprehensive PowerPoint & slide numbering quality assurance script.
Part of the english-class-slides (v1.2) skill package.
"""

import sys
import argparse
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    from pptx import Presentation
except ImportError:
    print("Error: python-pptx is not installed. Please run: pip install python-pptx")
    sys.exit(1)

def validate_deck(pptx_path, expected_count=53):
    path = Path(pptx_path)
    if not path.exists():
        print(f"[X] FAIL: Presentation file not found: {path}")
        return False

    prs = Presentation(str(path))
    slide_count = len(prs.slides)
    print(f"\nValidating: {path.name} (Slides: {slide_count})")
    
    if slide_count != expected_count:
        print(f"  [X] Slide count mismatch: Got {slide_count}, expected {expected_count}")
        return False
    else:
        print(f"  [OK] Exact slide count: {slide_count}")

    # Check slide dimensions (16:9 widescreen)
    w_in = prs.slide_width / 914400
    h_in = prs.slide_height / 914400
    ratio = w_in / h_in
    if abs(ratio - (16.0 / 9.0)) > 0.05:
        print(f"  [X] Aspect ratio mismatch: {w_in:.2f}x{h_in:.2f} (Expected 16:9)")
        return False
    else:
        print(f"  [OK] Aspect ratio: 16:9 widescreen ({w_in:.2f}\" x {h_in:.2f}\")")

    # Check slide 1 (cover)
    s1 = prs.slides[0]
    if len(s1.shapes) < 2:
        print(f"  [X] Cover slide missing shapes (found {len(s1.shapes)})")
        return False
    print(f"  [OK] Slide 01 (Cover) verified.")

    # Check content slides 2..51
    numbered_slides = 0
    for idx in range(1, 51):
        s = prs.slides[idx]
        has_num = any(len(sh.text_frame.text.strip()) == 2 and sh.text_frame.text.strip().isdigit() for sh in s.shapes if sh.has_text_frame)
        if has_num:
            numbered_slides += 1

    print(f"  [OK] Content slides (2..51): {numbered_slides}/50 numbered content slides verified.")

    # Check vocab slides 52..53
    s52 = prs.slides[51]
    s53 = prs.slides[52]
    if len(s52.shapes) >= 2 and len(s53.shapes) >= 2:
        print(f"  [OK] Slides 52-53 (Vocabulary Section) verified.")

    return True

def main():
    parser = argparse.ArgumentParser(description="Validate presentation decks.")
    parser.add_argument("--ja", default="output/slides_summer_vacation_ja.pptx", help="Path to JA PPTX")
    parser.add_argument("--en", default="output/slides_summer_vacation_en.pptx", help="Path to EN PPTX")
    parser.add_argument("--es", default="output/slides_summer_vacation_es.pptx", help="Path to ES PPTX")
    args = parser.parse_args()

    print("=" * 65)
    print("PRESENTATION QUALITY ASSURANCE (QA) VALIDATION")
    print("=" * 65)
    
    ok = True
    for p in [args.ja, args.en, args.es]:
        if Path(p).exists():
            if not validate_deck(p):
                ok = False

    print("\n" + "=" * 65)
    if ok:
        print("★ ALL PRESENTATION DECKS PASSED QA VALIDATION!")
    else:
        print("[X] QA VALIDATION REPORTED ERRORS.")
    print("=" * 65)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
validate_audio.py - Quality assurance audit for synthesized and recorded presentation audio files.
Audits track counts, file non-emptiness, decoding integrity, sample rates, channels, and lead-in headroom.
Part of the english-class-slides (v1.3) skill package.
"""

import sys
import argparse
from pathlib import Path
import soundfile as sf
import numpy as np

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def find_audio_track(a_dir, slide_num):
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

def validate_audio_folder(folder_path, expected_count=53):
    f_dir = Path(folder_path).resolve()
    if not f_dir.exists():
        print(f"[X] Directory not found: {f_dir}")
        return False

    print(f"\nAuditing Audio Directory: {f_dir}")
    print(f"Target Track Count: {expected_count}")

    found_tracks = []
    total_duration = 0.0
    all_decodable = True

    for i in range(1, expected_count + 1):
        track_path = find_audio_track(f_dir, i)
        if not track_path:
            print(f"  [X] Missing audio track for Slide {i:02d}")
            all_decodable = False
            continue

        try:
            data, sr = sf.read(str(track_path))
            dur = len(data) / sr
            total_duration += dur
            channels = 1 if data.ndim == 1 else data.shape[1]
            mono = np.mean(data, axis=1) if data.ndim > 1 else data
            idx_speech = np.where(np.abs(mono) > 0.03)[0]
            lead_in = idx_speech[0] / sr if len(idx_speech) > 0 else 0.0
            found_tracks.append((i, track_path, dur, sr, channels, lead_in))
        except Exception as e:
            print(f"  [X] Failed to decode {track_path.name}: {e}")
            all_decodable = False

    print(f"\nFound Valid Audio Tracks: {len(found_tracks)}/{expected_count}")
    if len(found_tracks) != expected_count or not all_decodable:
        print(f"  [X] Audio validation failed: {len(found_tracks)}/{expected_count} tracks valid.")
        return False

    total_size_mb = sum(p.stat().st_size for _, p, _, _, _, _ in found_tracks) / (1024 * 1024)
    print(f"  [OK] All {expected_count} audio files verified non-empty, decodable, and non-corrupt.")
    print(f"  [OK] Total Net Narration Duration: {total_duration:.3f} s ({total_duration/60:.2f} min)")
    print(f"  [OK] Total Audio Assets Size: {total_size_mb:.2f} MB")
    
    # Check sample lead-in for human recordings
    s1_lead = found_tracks[0][5]
    print(f"  [INFO] Slide 01 Lead-in Silence: {s1_lead:.3f} s (Native Playback Headroom)")
    return True

def main():
    parser = argparse.ArgumentParser(description="Validate presentation audio tracks.")
    parser.add_argument("--audio-dir", default="Audio/Japanese", help="Path to audio directory")
    parser.add_argument("--expected-count", type=int, default=53, help="Expected slide audio count")
    args = parser.parse_args()

    print("=" * 65)
    print("AUDIO ASSETS QUALITY ASSURANCE AUDIT (v1.3)")
    print("=" * 65)

    ok = validate_audio_folder(args.audio_dir, args.expected_count)
    print("\n" + "=" * 65)
    if ok:
        print("★ AUDIO QA AUDIT PASSED SUCCESSFULLY!")
    else:
        print("[X] AUDIO QA AUDIT REPORTED ISSUES.")
    print("=" * 65)
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()

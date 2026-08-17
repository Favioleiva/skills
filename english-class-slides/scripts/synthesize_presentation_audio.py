#!/usr/bin/env python3
"""
synthesize_presentation_audio.py - Synthesizes presentation audio with query validation and clean pre/post padding.
Part of the english-class-slides (v1.2) skill package.
"""

import os
import sys
import re
import json
import time
import subprocess
import argparse
from pathlib import Path
import requests
import imageio_ffmpeg

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_kana_slides(filepath):
    content = Path(filepath).read_text(encoding="utf-8")
    slides = re.split(r"(?:スライド)\s+(\d+)", content)
    parsed_dict = {}
    for i in range(1, len(slides), 2):
        s_num = int(slides[i])
        s_text = slides[i+1].strip()
        parsed_dict[s_num] = s_text

    slide_texts = []
    for i in range(1, len(parsed_dict) + 1):
        tb = parsed_dict[i]
        if i == 1:
            title, subtitle, author = "", "", ""
            for l in tb.split("\n"):
                if l.startswith("タイトル:"): title = l.replace("タイトル:", "").strip().replace(" ", "").replace("　", "")
                elif l.startswith("サブタイトル:"): subtitle = l.replace("サブタイトル:", "").strip().replace(" ", "").replace("　", "")
                elif l.startswith("著者:"): author = l.replace("著者:", "").strip().replace(" ", "").replace("　", "")
            spoken = f"{title}。{subtitle}。{author}。"
        elif 2 <= i <= len(parsed_dict) - 2:
            spoken = ""
            for l in tb.split("\n"):
                if l.startswith("本文:"):
                    spoken = l.replace("本文:", "").strip().replace(" ", "").replace("　", "")
                    break
        else:
            title = ""
            words = []
            for l in tb.split("\n"):
                l = l.strip()
                if l.startswith("タイトル:"): title = l.replace("タイトル:", "").strip().replace(" ", "").replace("　", "")
                elif re.match(r"^\d+\.\s*", l):
                    item = re.sub(r"^\d+\.\s*", "", l).strip()
                    item_clean = item.replace("—", "、").replace(" ", "").replace("　", "").strip()
                    words.append(item_clean)
            spoken = f"{title}。" + "。".join(words) + "。"
        slide_texts.append(spoken)
    return slide_texts

def synthesize_slide(host, speaker_id, text, out_mp3_path, ffmpeg_exe, bitrate="128k", save_raw_wav=None, pre_roll=0.10, post_roll=0.10):
    query_resp = requests.post(f"{host}/audio_query", params={"text": text, "speaker": speaker_id}, timeout=60)
    query = query_resp.json()

    # Query Validation
    if not query.get("kana"):
        raise ValueError(f"VOICEVOX query failed to produce kana for text: {text}")

    query["speedScale"] = 0.95
    query["pitchScale"] = 0.0
    query["intonationScale"] = 1.0
    query["volumeScale"] = 1.0
    query["prePhonemeLength"] = pre_roll
    query["postPhonemeLength"] = post_roll

    wav_resp = requests.post(
        f"{host}/synthesis",
        params={"speaker": speaker_id},
        data=json.dumps(query),
        headers={"Content-Type": "application/json"},
        timeout=120
    )
    raw_wav_bytes = wav_resp.content

    if save_raw_wav:
        Path(save_raw_wav).write_bytes(raw_wav_bytes)

    cmd = [
        ffmpeg_exe, "-y",
        "-hide_banner", "-loglevel", "error",
        "-i", "pipe:0",
        "-vn", "-codec:a", "libmp3lame",
        "-b:a", bitrate,
        str(out_mp3_path)
    ]
    res = subprocess.run(cmd, input=raw_wav_bytes, capture_output=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {res.stderr.decode('utf-8', errors='replace')}")

def main():
    parser = argparse.ArgumentParser(description="Synthesize Japanese presentation slides audio via VOICEVOX.")
    parser.add_argument("--kana-file", default="output/slides_reading_ja_kana.txt", help="Path to kana reading file")
    parser.add_argument("--output-dir", default="Audio/Japanese", help="Output directory for MP3 files")
    parser.add_argument("--host", default="http://127.0.0.1:50021", help="VOICEVOX host URL")
    parser.add_argument("--speaker-id", type=int, default=13, help="Speaker ID (default: 13 Aoyama Ryusei)")
    parser.add_argument("--force-all", action="store_true", help="Force regenerate all slides")
    parser.add_argument("--test-mode", action="store_true", help="Run test mode on sample slides (1, 2, 10, 30)")
    parser.add_argument("--pre-roll", type=float, default=0.50, help="Native pre-roll silence in seconds (default: 0.50)")
    parser.add_argument("--post-roll", type=float, default=0.50, help="Native post-roll silence in seconds (default: 0.50)")
    args = parser.parse_args()

    print("=" * 65)
    print("PRESENTATION AUDIO SYNTHESIZER (VOICEVOX Engine)")
    print("=" * 65)

    try:
        ver_res = requests.get(f"{args.host}/version", timeout=3)
        if ver_res.status_code == 200:
            print(f"[OK] Connected to VOICEVOX Engine (v{ver_res.text.strip()})")
    except Exception:
        print(f"[X] ERROR: Could not connect to VOICEVOX Engine at {args.host}.")
        sys.exit(1)

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slide_texts = parse_kana_slides(args.kana_file)
    print(f"[+] Loaded {len(slide_texts)} continuous-kana slide entries.\n")

    target_indices = [1, 2, 10, 30] if args.test_mode else list(range(1, len(slide_texts) + 1))
    start_time = time.time()
    generated = 0

    for idx in target_indices:
        text = slide_texts[idx - 1]
        out_mp3 = out_dir / f"slide_{idx:02d}.mp3"
        print(f"  [{idx:02d}/{len(slide_texts)}] Synthesizing {out_mp3.name}...")
        synthesize_slide(
            host=args.host,
            speaker_id=args.speaker_id,
            text=text,
            out_mp3_path=out_mp3,
            ffmpeg_exe=ffmpeg_exe,
            pre_roll=args.pre_roll,
            post_roll=args.post_roll
        )
        generated += 1

    elapsed = time.time() - start_time
    print(f"\n[OK] Synthesized {generated} slides in {elapsed:.1f}s!")
    print("=" * 65)

if __name__ == "__main__":
    main()

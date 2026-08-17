"""
synthesize_presentation_audio.py (english-class-slides v1.1)

Synthesizes presentation audio from slides_reading_ja_kana.txt via VOICEVOX API
(runs locally against RTX 3060 GPU or remote/Colab tunnel at 127.0.0.1:50021).
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
import requests

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

def parse_kana_slides(kana_file_path):
    with open(kana_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    raw_slides = re.split(r"(?:スライド)\s+(\d+)", content)
    parsed_dict = {}
    for i in range(1, len(raw_slides), 2):
        s_num = int(raw_slides[i])
        parsed_dict[s_num] = raw_slides[i+1].strip()

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
        elif 2 <= i <= 51:
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

def pad_wav_pcm(raw_wav_bytes, pre_sec=0.500, post_sec=0.500):
    """
    Prepends and appends exact PCM digital silence to uncompressed WAV bytes.
    Does NOT slice, trim, normalize, or fade existing audio samples.
    """
    import io
    import wave
    with wave.open(io.BytesIO(raw_wav_bytes), 'rb') as wf_in:
        nchannels = wf_in.getnchannels()
        sampwidth = wf_in.getsampwidth()
        framerate = wf_in.getframerate()
        nframes = wf_in.getnframes()
        comptype = wf_in.getcomptype()
        compname = wf_in.getcompname()
        raw_pcm = wf_in.readframes(nframes)

    pre_frames = int(framerate * pre_sec)
    post_frames = int(framerate * post_sec)

    silence_pre = b'\x00' * (pre_frames * nchannels * sampwidth)
    silence_post = b'\x00' * (post_frames * nchannels * sampwidth)

    padded_pcm = silence_pre + raw_pcm + silence_post

    out_io = io.BytesIO()
    with wave.open(out_io, 'wb') as wf_out:
        wf_out.setnchannels(nchannels)
        wf_out.setsampwidth(sampwidth)
        wf_out.setframerate(framerate)
        wf_out.setcomptype(comptype, compname)
        wf_out.writeframes(padded_pcm)

    return out_io.getvalue()

def synthesize_slide(host, speaker_id, text, out_mp3_path, ffmpeg_exe, bitrate="128k", save_raw_wav=None, save_padded_wav=None):
    # 1. Query
    query_resp = requests.post(f"{host}/audio_query", params={"text": text, "speaker": speaker_id}, timeout=60)
    query = query_resp.json()
    query["speedScale"] = 0.95
    query["pitchScale"] = 0.0
    query["intonationScale"] = 1.0
    query["volumeScale"] = 1.0

    # 2. Universal 0.5s pre/post silence buffer for all slides
    query["prePhonemeLength"] = 0.50
    query["postPhonemeLength"] = 0.50

    # 3. Universal first-mora attack protection for all slides
    try:
        accent_phrases = query.get("accent_phrases", [])
        if accent_phrases and accent_phrases[0].get("moras"):
            first_mora = accent_phrases[0]["moras"][0]
            if first_mora.get("consonant") is not None or first_mora.get("consonant_length") is not None:
                curr_c = first_mora.get("consonant_length") or 0.0
                first_mora["consonant_length"] = max(curr_c, 0.12)
            curr_v = first_mora.get("vowel_length") or 0.0
            first_mora["vowel_length"] = max(curr_v, 0.15)
    except Exception:
        pass

    # 4. Synthesize uncompressed WAV bytes
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

    # 5. Convert uncompressed WAV to MP3 with clean FFmpeg
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
    parser.add_argument("--force-regenerate", nargs="*", type=int, default=[1], help="Slide IDs to force regenerate (default: 1)")
    args = parser.parse_args()

    print("=" * 65)
    print("PRESENTATION AUDIO SYNTHESIZER (VOICEVOX / RTX 3060)")
    print("=" * 65)
    print(f"Input Kana       : {args.kana_file}")
    print(f"Output Dir       : {args.output_dir}")
    print(f"Host URL         : {args.host}")
    print(f"Speaker ID       : {args.speaker_id}")
    print(f"Force Regenerate : {args.force_regenerate}")
    print("=" * 65)

    # Check connection
    try:
        ver_res = requests.get(f"{args.host}/version", timeout=3)
        if ver_res.status_code == 200:
            print(f"[OK] Connected to VOICEVOX Engine (v{ver_res.text.strip()})")
    except Exception:
        print(f"[X] ERROR: Could not connect to VOICEVOX Engine at {args.host}.")
        print("    Please start the engine using Google Colab or local DirectML/GPU runner.")
        sys.exit(1)

    ffmpeg_exe = get_ffmpeg()
    os.makedirs(args.output_dir, exist_ok=True)
    slide_texts = parse_kana_slides(args.kana_file)
    print(f"[+] Loaded {len(slide_texts)} continuous-kana slide entries.\n")

    force_set = set(args.force_regenerate)
    start_time = time.time()
    generated_count = 0
    skipped_count = 0

    for idx, text in enumerate(slide_texts, start=1):
        out_mp3 = Path(args.output_dir) / f"slide_{idx:02d}.mp3"
        if out_mp3.exists() and out_mp3.stat().st_size > 0 and idx not in force_set:
            skipped_count += 1
            continue

        print(f"  [{idx:02d}/{len(slide_texts)}] Synthesizing {out_mp3.name}...")
        synthesize_slide(
            host=args.host,
            speaker_id=args.speaker_id,
            text=text,
            out_mp3_path=out_mp3,
            ffmpeg_exe=ffmpeg_exe
        )
        generated_count += 1

    elapsed = time.time() - start_time
    print("\n" + "=" * 65)
    print(f"★ SYNTHESIS COMPLETE! Generated: {generated_count}, Skipped: {skipped_count}")
    print(f"★ Output Folder: {args.output_dir}")
    print(f"★ Elapsed Time: {elapsed:.1f} seconds")
    print("=" * 65)

if __name__ == "__main__":
    main()

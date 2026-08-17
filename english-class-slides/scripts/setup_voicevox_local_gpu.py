#!/usr/bin/env python3
"""
setup_voicevox_local_gpu.py - Inspects and launches local native VOICEVOX Engine with DirectML/GPU.
Zero Docker required. Part of the english-class-slides (v1.2) skill package.
"""

import os
import sys
import time
import subprocess
import argparse
from pathlib import Path
import requests

DEFAULT_ENGINE_DIR = Path("tools/windows-directml")
DEFAULT_HOST = "http://127.0.0.1:50021"

def check_engine_health(host):
    try:
        r = requests.get(f"{host}/version", timeout=1)
        if r.status_code == 200:
            return r.text.strip().strip('"')
    except Exception:
        pass
    return None

def main():
    parser = argparse.ArgumentParser(description="Ensure local VOICEVOX GPU Engine is running.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="VOICEVOX host URL")
    parser.add_argument("--engine-dir", default=str(DEFAULT_ENGINE_DIR), help="Directory containing run.exe")
    parser.add_argument("--use-gpu", action="store_true", default=True, help="Enable GPU acceleration")
    args = parser.parse_args()

    print("=" * 65)
    print("VOICEVOX ENGINE LOCAL RUNNER (DirectML / Native GPU)")
    print("=" * 65)

    ver = check_engine_health(args.host)
    if ver:
        print(f"[OK] VOICEVOX Engine is already running (v{ver}) on {args.host}!")
        return

    eng_path = Path(args.engine_dir).resolve()
    run_exe = eng_path / "run.exe"

    if not run_exe.exists():
        print(f"[X] Engine binary not found: {run_exe}")
        print("    Please download the official VOICEVOX DirectML release into tools/windows-directml/")
        sys.exit(1)

    print(f"Starting {run_exe.name} in background...")
    cmd = [str(run_exe), "--host", "127.0.0.1", "--port", "50021"]
    if args.use_gpu:
        cmd.append("--use_gpu")

    log_file = open("tools/voicevox_engine.log", "w", encoding="utf-8")
    proc = subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT, cwd=str(eng_path))
    print(f"Process spawned with PID {proc.pid}. Polling /version...")

    for sec in range(30):
        ver = check_engine_health(args.host)
        if ver:
            print(f"\n[OK] VOICEVOX Engine is ONLINE (v{ver}) on {args.host}!")
            print("=" * 65)
            return
        time.sleep(1)
        print(".", end="", flush=True)

    print(f"\n[X] Engine failed to respond within 30 seconds. Check tools/voicevox_engine.log")
    sys.exit(1)

if __name__ == "__main__":
    main()

"""
setup_voicevox_local_gpu.py (english-class-slides v1.1)

Automated installer and manager for local VOICEVOX Engine on Windows
using DirectML GPU acceleration (NVIDIA RTX 3060 compatible) — Zero Docker required.
"""

import os
import subprocess
import sys
import time
import requests
from pathlib import Path

VERSION = "0.25.2"
ENGINE_DIR = Path("tools/voicevox_engine").resolve()
HOST = "http://127.0.0.1:50021"

def check_engine_online():
    try:
        r = requests.get(f"{HOST}/version", timeout=2)
        if r.status_code == 200:
            return r.text.strip().strip('"')
    except Exception:
        pass
    return None

def main():
    print("=" * 65)
    print("LOCAL VOICEVOX ENGINE MANAGER (NVIDIA RTX 3060 / DirectML)")
    print("=" * 65)

    # 1. Check if already online
    current_ver = check_engine_online()
    if current_ver:
        print(f"[OK] VOICEVOX Engine is ALREADY ONLINE on port 50021!")
        print(f"     Version: {current_ver}")
        return True

    # 2. Check if installed
    run_exe = ENGINE_DIR / "run.exe"
    if not run_exe.exists():
        print(f"\n[1/3] DOWNLOADING OFFICIAL WINDOWS DIRECTML GPU RELEASE (v{VERSION})...")
        ENGINE_DIR.mkdir(parents=True, exist_ok=True)
        zip_url = f"https://github.com/VOICEVOX/voicevox_engine/releases/download/{VERSION}/voicevox_engine-windows-directml-{VERSION}.7z.001"
        archive_path = ENGINE_DIR.parent / f"voicevox_engine-windows-directml-{VERSION}.7z.001"

        if not archive_path.exists():
            print(f"  Fetching: {zip_url}")
            try:
                import urllib.request
                urllib.request.urlretrieve(zip_url, str(archive_path))
                print(f"  Downloaded: {archive_path.stat().st_size / (1024*1024):.1f} MB")
            except Exception as e:
                print(f"  [X] Download failed: {e}")
                return False

        print(f"\n[2/3] EXTRACTING ENGINE ARCHIVE...")
        # Try 7z / tar / powershell
        extract_cmd = ["tar", "-xf", str(archive_path), "-C", str(ENGINE_DIR.parent)]
        res = subprocess.run(extract_cmd, capture_output=True)
        if res.returncode != 0:
            print(f"  Extraction note: {res.stderr.decode('utf-8', errors='replace')}")

    if run_exe.exists():
        print(f"\n[3/3] STARTING VOICEVOX ENGINE (DirectML GPU Accelerated)...")
        log_file = open(ENGINE_DIR / "engine.log", "w", encoding="utf-8")
        proc = subprocess.Popen([str(run_exe), "--host", "127.0.0.1", "--port", "50021"],
                                cwd=str(ENGINE_DIR), stdout=log_file, stderr=subprocess.STDOUT)
        print(f"  Process started with PID: {proc.pid}")

        # Poll /version
        for sec in range(30):
            v = check_engine_online()
            if v:
                print(f"\n[★ ONLINE] VOICEVOX Engine ready! Version: {v}")
                return True
            time.sleep(1)

    print(f"\n[NOTE] If local engine binary is not yet extracted, you can start VOICEVOX desktop or run the engine on {HOST}.")
    return False

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""LiveVault: bounded capture of an accessible public TikTok LIVE stream."""
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from urllib.request import Request, urlopen

CREATOR = os.getenv("CREATOR", "").lstrip("@").strip()
MAX_SECONDS = 5 * 3600 + 20 * 60
MAX_BYTES = 400 * 1024 * 1024
RESOLVER = "https://livevault-tiktok-recorder.vercel.app/api/resolve?username="
OUT = Path("recordings")

def main():
    if not re.fullmatch(r"[A-Za-z0-9._]{1,24}", CREATOR):
        raise ValueError("Creator username must contain 1-24 letters, numbers, dots or underscores.")
    OUT.mkdir(exist_ok=True)
    request = Request(RESOLVER + CREATOR, headers={"User-Agent": "LiveVault/1.0"})
    with urlopen(request, timeout=35) as response:
        payload = json.load(response)
    if not payload.get("live") or not payload.get("url"):
        raise RuntimeError("Creator is offline or no accessible stream is available.")
    stream_url = payload["url"]
    if not stream_url.startswith("https://"):
        raise RuntimeError("Recorder requires an HTTPS stream.")
    video_path = str(OUT / (CREATOR + "_%03d.mkv"))
    cmd = [
        "ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "warning",
        "-rw_timeout", "30000000",
        "-user_agent", "Mozilla/5.0 (LiveVault public stream archival)",
        "-i", stream_url,
        "-map", "0:v?", "-map", "0:a?",
        "-c", "copy",
        "-f", "segment", "-segment_time", "900",
        "-reset_timestamps", "1",
        "-segment_format", "matroska", video_path,
    ]
    print(f"Starting recording for @{CREATOR}. Video segments save as MKV.", flush=True)
    process = subprocess.Popen(cmd)
    started = time.monotonic()
    stopped_for_limit = False
    try:
        while process.poll() is None:
            size = sum(p.stat().st_size for p in OUT.glob("*.mkv"))
            if size >= MAX_BYTES or time.monotonic() - started >= MAX_SECONDS:
                print("Free-tier size/time budget reached. Finalizing video files.", flush=True)
                process.send_signal(signal.SIGINT)
                stopped_for_limit = True
                break
            time.sleep(5)
        try:
            process.wait(timeout=90)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    except BaseException:
        if process.poll() is None:
            process.send_signal(signal.SIGINT)
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
        raise
    saved = sorted(OUT.glob("*.mkv"))
    nonempty = [p for p in saved if p.stat().st_size > 0]
    print(f"Saved {len(nonempty)} segment(s), {sum(p.stat().st_size for p in nonempty)} bytes.", flush=True)
    if not nonempty:
        raise RuntimeError("No playable stream data was captured.")
    if process.returncode != 0 and not stopped_for_limit:
        print("Stream interrupted; uploading any captured files.", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()

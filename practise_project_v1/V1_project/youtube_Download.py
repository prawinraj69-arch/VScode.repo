"""
Download YouTube audio as MP3 (requires ffmpeg on PATH).

Usage:
    python youtube_Download.py
    python youtube_Download.py "https://youtu.be/VIDEO_ID"
    python youtube_Download.py "https://youtube.com/playlist?list=..."
"""

from __future__ import annotations
import argparse
from pathlib import Path
import sys
import subprocess
import shutil


try:
    from yt_dlp import YoutubeDL
except Exception:
    print("Required package 'yt-dlp' not found. Attempting to install...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
        from yt_dlp import YoutubeDL
    except Exception as exc:
        print("Automatic installation failed. Please run: pip install yt-dlp")
        raise SystemExit(exc)


DEFAULT_VIDEO_URL = "https://youtube.com/playlist?list=PL4kM7CQB-CQOGe-vOPNvHsMMAwF9IH4Nk&si=HnA8eSji9aUFCFm5"


def check_ffmpeg() -> None:
    if not (shutil.which("ffmpeg") or shutil.which("ffprobe")):
        print("ERROR: ffmpeg not found on PATH.")
        print("MP3 conversion requires ffmpeg. Install it from https://ffmpeg.org/download.html")
        print("Then add ffmpeg to your system PATH and retry.")
        raise SystemExit(1)


def download_audio(url: str) -> None:
    check_ffmpeg()

    save_path = Path(__file__).resolve().parent

    ydl_opts = {
        "outtmpl": str(save_path / "%(title)s [%(id)s].%(ext)s"),
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": False,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if isinstance(info, dict) and info.get("_type") == "playlist":
                count = len(info.get("entries") or [])
                print(f"\nDownloaded {count} track(s) from playlist: {info.get('title', '')}")
            else:
                raw = ydl.prepare_filename(info)
                mp3_path = Path(raw).with_suffix(".mp3")
                print(f"\nSaved: {mp3_path}")

    except Exception as exc:
        print(f"Download failed: {exc}")
        raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download YouTube audio as MP3")
    parser.add_argument(
        "url",
        nargs="?",
        default=DEFAULT_VIDEO_URL,
        help="YouTube URL (video or playlist). Defaults to DEFAULT_VIDEO_URL.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"Downloading: {args.url}")
    download_audio(args.url)

#!/usr/bin/env python3
"""
youtube_launcher.py

Usage:
    python youtube_launcher.py               -> opens YouTube homepage
    python youtube_launcher.py <video_url>   -> opens specific video
"""

import webbrowser
import sys
import requests

# OPTIONAL: if you have a proxy server, put it here
PROXY = None  # Example: "http://127.0.0.1:8080"

def check_youtube(proxy=None):
    url = "https://www.youtube.com/"
    try:
        if proxy:
            proxies = {"http": proxy, "https": proxy}
            r = requests.get(url, proxies=proxies, timeout=10)
        else:
            r = requests.get(url, timeout=10)
        return r.status_code == 200
    except Exception:
        return False

def open_youtube(url="https://www.youtube.com"):
    print(f"Opening: {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    # If a video link is provided, use that
    if len(sys.argv) > 1:
        yt_url = sys.argv[1]
    else:
        yt_url = "https://www.youtube.com"

    # Check if YouTube is reachable
    print("Checking YouTube access...")
    if check_youtube(PROXY):
        open_youtube(yt_url)
    else:
        print("⚠️ YouTube seems blocked on your network.")
        if PROXY:
            print(f"Try enabling proxy: {PROXY}")
        else:
            print("You may need a VPN or proxy to access YouTube.")

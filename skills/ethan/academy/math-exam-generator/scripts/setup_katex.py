#!/usr/bin/env python3
"""
setup_katex.py — Download KaTeX files locally for offline Playwright PDF rendering.
Only needs to run once per machine. Safe to re-run (skips existing files).

Usage:
    python3 setup_katex.py
    python3 setup_katex.py --out /custom/path
"""

import argparse
import os
import re
import urllib.request

DEFAULT_OUT = os.path.expanduser("~/.openclaw/workspace/homework/katex-local")
BASE = "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist"

FILES = [
    "katex.min.js",
    "katex.min.css",
    "contrib/auto-render.min.js",
]

FONTS = [
    "KaTeX_Main-Regular.woff2", "KaTeX_Main-Bold.woff2", "KaTeX_Main-Italic.woff2",
    "KaTeX_Math-Italic.woff2",
    "KaTeX_Size1-Regular.woff2", "KaTeX_Size2-Regular.woff2",
    "KaTeX_Size3-Regular.woff2", "KaTeX_Size4-Regular.woff2",
    "KaTeX_AMS-Regular.woff2",
    "KaTeX_Caligraphic-Regular.woff2", "KaTeX_Fraktur-Regular.woff2",
    "KaTeX_SansSerif-Regular.woff2", "KaTeX_Script-Regular.woff2",
    "KaTeX_Typewriter-Regular.woff2",
]


def download(url, dest):
    if os.path.exists(dest):
        print(f"  skip  {os.path.basename(dest)}")
        return
    urllib.request.urlretrieve(url, dest)
    print(f"  ✅    {os.path.basename(dest)}")


def patch_css(out_dir):
    css_path = os.path.join(out_dir, "katex.min.css")
    local_css = os.path.join(out_dir, "katex.local.css")
    if os.path.exists(local_css):
        print("  skip  katex.local.css (already patched)")
        return local_css
    fonts_abs = os.path.join(out_dir, "fonts")
    with open(css_path) as f:
        css = f.read()
    css_fixed = re.sub(
        r"url\(fonts/([^)]+)\)",
        lambda m: f"url(file://{fonts_abs}/{m.group(1)})",
        css,
    )
    with open(local_css, "w") as f:
        f.write(css_fixed)
    print(f"  ✅    katex.local.css (patched font paths)")
    return local_css


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()

    out = args.out
    fonts_dir = os.path.join(out, "fonts")
    os.makedirs(fonts_dir, exist_ok=True)

    print(f"\n📦 KaTeX setup → {out}\n")

    print("Downloading JS/CSS:")
    for f in FILES:
        download(f"{BASE}/{f}", os.path.join(out, os.path.basename(f)))

    print("\nDownloading fonts:")
    for f in FONTS:
        download(f"{BASE}/fonts/{f}", os.path.join(fonts_dir, f))

    print("\nPatching CSS for offline use:")
    patch_css(out)

    print(f"\n✅ KaTeX ready at: {out}")
    print("   katex.min.js, katex.local.css, auto-render.min.js, fonts/\n")


if __name__ == "__main__":
    main()

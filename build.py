#!/usr/bin/env python3
"""
build.py
=========
Main build script. Run this to regenerate the entire site.

Usage:
    python build.py

Config files read:
    config/main.yaml         — site metadata, nav, theme
    config/photography.yaml  — photography page content
    config/blog.yaml         — blog page content

Output:
    output/index.html
    output/photography.html
    output/blog.html

All config lives in config/*.yaml — you never need to touch any Python file.
"""

import os
import sys
import shutil

# ── Ensure the project root is on sys.path ──────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required.  Run: pip install pyyaml")
    sys.exit(1)


# ── Load configs ─────────────────────────────────────────────────────────────

def load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def load_configs():
    cfg       = load(os.path.join(ROOT, "config", "main.yaml"))
    photo_cfg = load(os.path.join(ROOT, "config", "photography.yaml"))
    blog_cfg  = load(os.path.join(ROOT, "config", "blog.yaml"))
    return cfg, photo_cfg, blog_cfg


# ── Build ────────────────────────────────────────────────────────────────────

def build():
    cfg, photo_cfg, blog_cfg = load_configs()

    out_dir = os.path.join(ROOT, cfg["site"].get("output_dir", "output"))
    os.makedirs(out_dir, exist_ok=True)

    from site_builder.pages.index_page import build_index
    from site_builder.pages.photo_page import build_photography
    from site_builder.pages.blog_page  import build_blog

    pages = [
        ("index.html",       build_index(cfg, photo_cfg, blog_cfg)),
        ("photography.html", build_photography(cfg, photo_cfg, blog_cfg)),
        ("blog.html",        build_blog(cfg, photo_cfg, blog_cfg)),
    ]

    for filename, html in pages:
        out_path = os.path.join(out_dir, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓  {filename}")

    # Copy images/ folder if it exists next to config
    img_src = os.path.join(ROOT, "images")
    img_dst = os.path.join(out_dir, "images")
    if os.path.isdir(img_src):
        if os.path.exists(img_dst):
            shutil.rmtree(img_dst)
        shutil.copytree(img_src, img_dst)
        print(f"  ✓  images/ copied")
    else:
        print(f"  ·  images/ folder not found — skipped (add your photos to images/)")

    print(f"\nBuild complete → {out_dir}/")
    print("Open output/index.html in a browser to preview.")


if __name__ == "__main__":
    print("Building site…")
    build()

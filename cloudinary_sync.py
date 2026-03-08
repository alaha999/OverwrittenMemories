#!/usr/bin/env python3
"""
cloudinary_sync.py
==================
Fetches all images from your Cloudinary account (or a specific folder/tag)
and writes/updates config/photography.yaml.

Key behaviour
-------------
* SAFE MERGE  — existing hand-edited fields (alt, category, location, year)
  are NEVER overwritten on re-runs.  Only brand-new images are appended.
* NEW IMAGES  — get a stub entry with the Cloudinary URL as `src`, the
  public_id as a placeholder `alt`, and any Cloudinary tags/context already
  attached to the asset.
* REMOVED IMAGES — entries whose Cloudinary asset no longer exists are
  commented out (not deleted), so you don't silently lose your captions.
* ORDERING  — new images are inserted sorted by Cloudinary upload date
  (newest first). Existing order is preserved for already-known images.

Usage
-----
    python cloudinary_sync.py               # sync + show diff summary
    python cloudinary_sync.py --dry-run     # print what would change, write nothing
    python cloudinary_sync.py --folder wedding/2024   # only a specific folder
    python cloudinary_sync.py --tag        website    # only images tagged "website"

Dependencies
------------
    pip install cloudinary pyyaml python-dotenv

Credentials
-----------
Create a .env file in the project root (it's gitignored):

    CLOUDINARY_CLOUD_NAME=your_cloud_name
    CLOUDINARY_API_KEY=your_api_key
    CLOUDINARY_API_SECRET=your_api_secret

Or set those as environment variables / GitHub Actions secrets.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))

# ── Dependency check ─────────────────────────────────────────────────────────

def _check_deps():
    missing = []
    for pkg, imp in [("pyyaml", "yaml"), ("cloudinary", "cloudinary"),
                     ("python-dotenv", "dotenv")]:
        try:
            __import__(imp)
        except ImportError:
            missing.append(pkg)
    if missing:
        print("ERROR: Missing dependencies. Install with:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)

_check_deps()

import yaml
import cloudinary
import cloudinary.api
from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

# ─────────────────────────────────────────────────────────────────────────────
# Cloudinary setup
# ─────────────────────────────────────────────────────────────────────────────

def configure_cloudinary():
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key    = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    missing = [k for k, v in {
        "CLOUDINARY_CLOUD_NAME": cloud_name,
        "CLOUDINARY_API_KEY":    api_key,
        "CLOUDINARY_API_SECRET": api_secret,
    }.items() if not v]

    if missing:
        print("ERROR: Missing Cloudinary credentials.")
        print("  Create a .env file in the project root with:")
        for k in missing:
            print(f"    {k}=your_value")
        print("  Or set them as environment variables.")
        sys.exit(1)

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )
    print(f"  Connected to Cloudinary cloud: {cloud_name}")


# ─────────────────────────────────────────────────────────────────────────────
# Fetch assets from Cloudinary
# ─────────────────────────────────────────────────────────────────────────────

def fetch_cloudinary_assets(folder: str | None = None,
                             tag: str | None = None) -> list[dict]:
    """
    Return all image resources from Cloudinary, newest-first.
    Handles pagination automatically (Cloudinary returns max 500 per page).
    """
    common_kwargs = dict(
        resource_type="image",
        type="upload",
        max_results=500,
        # Ask for tags and context (where caption/location etc. can be stored)
        tags=True,
        context=True,
        # Include metadata fields
        metadata=True,
    )

    assets = []
    next_cursor = None

    print(f"  Fetching assets from Cloudinary", end="")
    if folder:
        print(f" (folder: {folder})", end="")
    if tag:
        print(f" (tag: {tag})", end="")
    print("…")

    while True:
        if next_cursor:
            common_kwargs["next_cursor"] = next_cursor

        if folder:
            resp = cloudinary.api.resources_by_asset_folder(
                folder, **common_kwargs
            )
        elif tag:
            resp = cloudinary.api.resources_by_tag(tag, **common_kwargs)
        else:
            resp = cloudinary.api.resources(**common_kwargs)

        assets.extend(resp.get("resources", []))
        next_cursor = resp.get("next_cursor")
        if not next_cursor:
            break

    # Sort newest upload first
    assets.sort(
        key=lambda r: r.get("created_at", ""),
        reverse=True,
    )
    print(f"  Found {len(assets)} image(s) in Cloudinary")
    return assets


# ─────────────────────────────────────────────────────────────────────────────
# URL builder — optimised Cloudinary delivery URL
# ─────────────────────────────────────────────────────────────────────────────

def build_url(asset: dict) -> str:
    """
    Build an optimised Cloudinary delivery URL for the asset.
    Uses f_auto (format negotiation) and q_auto (quality optimisation).
    You can adjust the transformation string here if you want, e.g. add
    w_1600 to cap the width.
    """
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    public_id  = asset["public_id"]
    # Append extension only if not already in public_id
    fmt = asset.get("format", "jpg")
    if not public_id.endswith(f".{fmt}"):
        public_id_ext = f"{public_id}.{fmt}"
    else:
        public_id_ext = public_id

    return (
        f"https://res.cloudinary.com/{cloud_name}"
        f"/image/upload/f_auto,q_auto"
        f"/{public_id_ext}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Slug / alt helpers
# ─────────────────────────────────────────────────────────────────────────────

def _public_id_to_slug(public_id: str) -> str:
    """
    Turn a Cloudinary public_id into a readable placeholder alt string.
    e.g. "website/2024/street-corner-at-dusk" → "Street corner at dusk"
         "IMG_4521"                            → "IMG 4521"
    """
    # Take the last path segment
    name = public_id.split("/")[-1]
    # Remove extension if crept in
    name = re.sub(r"\.\w+$", "", name)
    # Replace separators with spaces
    name = re.sub(r"[-_]+", " ", name)
    return name.strip().capitalize()


def _context_value(asset: dict, key: str) -> str | None:
    """Read a value from Cloudinary's context dict (custom metadata)."""
    ctx = asset.get("context", {})
    # Cloudinary returns context as {"custom": {"key": "val"}} or flat
    if isinstance(ctx, dict):
        custom = ctx.get("custom", ctx)
        return custom.get(key) or None
    return None


def _extract_year(asset: dict) -> int | None:
    """Try to get year from Cloudinary created_at timestamp."""
    created = asset.get("created_at", "")
    if created:
        try:
            return datetime.fromisoformat(created.rstrip("Z")).year
        except ValueError:
            pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# YAML I/O
# ─────────────────────────────────────────────────────────────────────────────

YAML_PATH = ROOT / "config" / "photography.yaml"

def load_existing_yaml() -> dict:
    if not YAML_PATH.exists():
        return {}
    with open(YAML_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _safe_str(s) -> str:
    s = str(s)
    needs_quote = any(c in s for c in ':#{}&*!|>\'"%@`[]')
    if needs_quote:
        return '"' + s.replace('"', '\\"') + '"'
    return s


def write_yaml(photography: dict, dry_run: bool = False) -> str:
    """
    Serialise the photography dict back to a clean, human-readable YAML
    string preserving comment headers.
    """
    ph     = photography.get("photography", photography)
    images = ph.get("images", [])

    lines = [
        "# photography.yaml",
        "# Generated / updated by cloudinary_sync.py",
        f"# Last synced: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "#",
        "# Fields you should fill in for each new image:",
        "#   alt      : caption shown in the lightbox and used as alt text",
        "#   category : list of tags from the categories list above",
        "#   location : where the photo was taken",
        "#   year     : year the photo was taken",
        "#",
        "# DO NOT change the `src` field — it is the Cloudinary delivery URL.",
        "# DO NOT change the `public_id` field — it links back to Cloudinary.",
        "",
        "photography:",
        f"  page_title:  {_safe_str(ph.get('page_title', 'Photography'))}",
        f"  eyebrow:     {_safe_str(ph.get('eyebrow', 'Visual Journal'))}",
        "  intro: >",
        f"    {ph.get('intro', '').strip()}",
        "",
        f"  grid_columns: {ph.get('grid_columns', 4)}",
        "",
        "  categories:",
    ]
    for cat in ph.get("categories", ["all"]):
        lines.append(f"    - {_safe_str(cat)}")

    lines += [
        "",
        "  images:",
    ]

    for img in images:
        removed = img.get("_removed", False)
        prefix  = "    # REMOVED — no longer in Cloudinary:\n    # " if removed else "    "

        cats = img.get("category", [])
        if isinstance(cats, str):
            cats = [cats]
        cats_str = "[" + ", ".join(_safe_str(c) for c in cats) + "]" if cats else "[]"

        block = [
            f"    - src:       {_safe_str(img.get('src', ''))}",
            f"      public_id: {_safe_str(img.get('public_id', ''))}",
            f"      alt:       {_safe_str(img.get('alt', ''))}",
            f"      category:  {cats_str}",
        ]
        if img.get("location"):
            block.append(f"      location:  {_safe_str(img['location'])}")
        if img.get("year"):
            block.append(f"      year:      {img['year']}")
        block.append("")   # blank line between entries

        if removed:
            # Comment out every line
            lines.append("    # REMOVED — no longer in Cloudinary:")
            for bl in block:
                lines.append("    # " + bl.lstrip())
        else:
            lines.extend(block)

    result = "\n".join(lines)

    if dry_run:
        print("\n── photography.yaml (dry-run preview) ──────────────────")
        print(result[:3000] + ("\n…(truncated)" if len(result) > 3000 else ""))
        print("────────────────────────────────────────────────────────")
    else:
        YAML_PATH.parent.mkdir(parents=True, exist_ok=True)
        YAML_PATH.write_text(result, encoding="utf-8")
        print(f"  ✓  Wrote {YAML_PATH.relative_to(ROOT)}")

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Merge logic  (the heart of the script)
# ─────────────────────────────────────────────────────────────────────────────

def merge(existing_yaml: dict, cloudinary_assets: list[dict]) -> tuple[dict, dict]:
    """
    Merge Cloudinary assets into the existing YAML, returning:
      (updated_photography_dict, stats_dict)

    Rules:
      - Existing entries: NEVER overwrite user-edited fields.
        Only `src` is refreshed (in case you renamed/moved the asset).
      - New assets: appended with stub metadata extracted from Cloudinary
        (tags → category, context caption → alt, context location → location).
      - Assets no longer in Cloudinary: marked _removed=True (commented out).
    """
    ph = deepcopy(existing_yaml.get("photography", {}))
    if not ph:
        # Bootstrap from scratch
        ph = {
            "page_title":  "Photography",
            "eyebrow":     "Visual Journal",
            "intro":       "A collection of moments.",
            "grid_columns": 4,
            "categories":  ["all"],
            "images":      [],
        }

    existing_images: list[dict] = ph.get("images", [])

    # Index existing entries by public_id for O(1) lookup
    # Also index by src URL as a fallback (for entries without public_id)
    by_pid  = {img["public_id"]: img for img in existing_images if img.get("public_id")}
    by_src  = {img["src"]: img       for img in existing_images if img.get("src")}
    cloud_pids = {a["public_id"] for a in cloudinary_assets}

    stats = {"added": 0, "updated": 0, "removed": 0, "unchanged": 0}

    new_entries: list[dict] = []   # truly new assets, prepended

    for asset in cloudinary_assets:
        pid = asset["public_id"]
        url = build_url(asset)

        # ── Already known by public_id ──
        if pid in by_pid:
            entry = by_pid[pid]
            # Refresh URL (transformation string may have changed)
            if entry.get("src") != url:
                entry["src"] = url
                stats["updated"] += 1
            else:
                stats["unchanged"] += 1
            # Clear any _removed flag
            entry.pop("_removed", None)
            continue

        # ── Known by URL but missing public_id (old entries) ──
        if url in by_src:
            entry = by_src[url]
            entry["public_id"] = pid
            entry.pop("_removed", None)
            stats["updated"] += 1
            continue

        # ── Brand new asset ──
        # Extract what we can from Cloudinary metadata
        cld_tags     = asset.get("tags", [])
        cld_alt      = (_context_value(asset, "caption")
                        or _context_value(asset, "alt")
                        or _public_id_to_slug(pid))
        cld_location = (_context_value(asset, "location")
                        or _context_value(asset, "credit")
                        or None)
        cld_year     = _extract_year(asset)

        new_entry: dict = {
            "src":       url,
            "public_id": pid,
            "alt":       cld_alt,
            "category":  cld_tags if cld_tags else [],
        }
        if cld_location:
            new_entry["location"] = cld_location
        if cld_year:
            new_entry["year"] = cld_year

        new_entries.append(new_entry)
        stats["added"] += 1

    # ── Mark removed assets ──
    for entry in existing_images:
        pid = entry.get("public_id")
        if pid and pid not in cloud_pids and not entry.get("_removed"):
            entry["_removed"] = True
            stats["removed"] += 1

    # Prepend new entries (newest Cloudinary upload → top of list)
    ph["images"] = new_entries + existing_images
    return {"photography": ph}, stats


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Sync Cloudinary → config/photography.yaml"
    )
    parser.add_argument(
        "--folder",   metavar="FOLDER",
        help="Only fetch images from this Cloudinary folder (e.g. website/2024)"
    )
    parser.add_argument(
        "--tag",      metavar="TAG",
        help="Only fetch images with this Cloudinary tag (e.g. website)"
    )
    parser.add_argument(
        "--dry-run",  action="store_true",
        help="Show what would change without writing anything"
    )
    parser.add_argument(
        "--no-build", action="store_true",
        help="Skip running build.py after syncing"
    )
    args = parser.parse_args()

    print("=" * 55)
    print("  Cloudinary → photography.yaml sync")
    print("=" * 55)

    configure_cloudinary()

    # 1. Fetch from Cloudinary
    assets = fetch_cloudinary_assets(folder=args.folder, tag=args.tag)
    if not assets:
        print("  No assets returned — check your folder/tag filter or credentials.")
        sys.exit(0)

    # 2. Load existing YAML (preserves all hand-edited captions)
    existing = load_existing_yaml()
    print(f"  Existing YAML: {len(existing.get('photography', {}).get('images', []))} entries")

    # 3. Merge
    updated, stats = merge(existing, assets)

    # 4. Report
    print(f"\n  Sync summary:")
    print(f"    + {stats['added']}     new images added")
    print(f"    ~ {stats['updated']}   URLs refreshed")
    print(f"    ✓ {stats['unchanged']} unchanged")
    if stats["removed"]:
        print(f"    ✗ {stats['removed']}   removed (commented out in YAML)")

    # 5. Write YAML
    if not args.dry_run:
        write_yaml(updated)
    else:
        write_yaml(updated, dry_run=True)
        print("\n  [dry-run] No files were written.")
        sys.exit(0)

    # 6. Rebuild site
    if not args.no_build:
        print("\nRebuilding site…")
        import build as site_build
        site_build.build()
    else:
        print("\nSkipping build (--no-build). Run python build.py when ready.")


if __name__ == "__main__":
    main()

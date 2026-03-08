"""
site_builder/styles.py
========================
Shared CSS variables, reset, typography, and the HTML <head> template.
Everything is driven by the theme section of main.yaml.
"""
from __future__ import annotations


def build_css_vars(theme: dict) -> str:
    """Emit :root and [data-theme=dark] CSS variable blocks from the theme dict."""
    def block(mode_cfg: dict, selector: str) -> str:
        lines = [f"{selector} {{"]
        mapping = {
            "--bg":           "bg",
            "--bg2":          "bg2",
            "--surface":      "surface",
            "--border":       "border",
            "--text":         "text",
            "--text-muted":   "text_muted",
            "--text-dim":     "text_dim",
            "--accent":       "accent",
            "--accent-mid":   "accent_mid",
            "--accent-light": "accent_light",
        }
        for var, key in mapping.items():
            lines.append(f"  {var}: {mode_cfg[key]};")
        lines.append("}")
        return "\n".join(lines)

    light = block(theme["light"], ":root")
    dark  = block(theme["dark"],  "[data-theme=dark]")
    return f"{light}\n{dark}"


SHARED_CSS_TEMPLATE = """\
{css_vars}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
  --max: 1400px;
  --serif: 'Lora', 'Georgia', serif;
  --sans:  'DM Sans', sans-serif;
  --mono:  'JetBrains Mono', 'Fira Mono', monospace;
  --nav-h: 58px;
  --transition: background .25s ease, color .25s ease, border-color .25s ease;
}}

html {{ scroll-behavior: smooth; }}

body {{
  font-family: var(--sans);
  background: var(--bg);
  color: var(--text);
  transition: var(--transition);
  min-height: 100vh;
  line-height: 1.6;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: var(--bg2); }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--accent-mid); }}

/* ── Selection ── */
::selection {{ background: var(--accent-light); color: var(--accent); }}

/* ── Animations ── */
@keyframes fade-up {{
  from {{ opacity: 0; transform: translateY(16px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes fade-in {{
  from {{ opacity: 0; }}
  to   {{ opacity: 1; }}
}}
@keyframes scale-in {{
  from {{ opacity: 0; transform: scale(.96); }}
  to   {{ opacity: 1; transform: scale(1); }}
}}
"""


HTML_HEAD_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en" data-theme="{default_mode}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;1,400&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
{shared_css}
{page_css}
  </style>
</head>
<body>
"""

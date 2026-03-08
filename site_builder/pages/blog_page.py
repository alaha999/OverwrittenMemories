"""
site_builder/pages/blog_page.py
=================================
Builds blog.html — collapsible post cards in a grid, collapse-all control.
"""
from __future__ import annotations
import html as _html
import json


def esc(s: str) -> str:
    return _html.escape(str(s), quote=True)


BLOG_CSS = """
/* ── Blog page ── */
.blog-page { padding: 44px 18px 60px; max-width: var(--max); margin: 0 auto; animation: fade-up .5s ease both; }

.page-eyebrow {
  font-family: var(--mono); font-size: .68rem; letter-spacing: .16em;
  text-transform: uppercase; color: var(--accent-mid);
  margin-bottom: 10px; display: flex; align-items: center; gap: 12px;
}
.page-eyebrow::before { content: ''; display: block; width: 28px; height: 1px; background: var(--accent-mid); }
.page-title {
  font-family: var(--serif); font-size: 2.2rem; font-weight: 400;
  color: var(--text); letter-spacing: -.01em; margin-bottom: 10px;
}
.page-intro {
  font-size: .92rem; color: var(--text-muted); max-width: 520px;
  line-height: 1.85; margin-bottom: 36px;
}

/* ── Collapse controls toolbar ── */
.blog-toolbar {
  display: flex; justify-content: flex-end; margin-bottom: 20px; gap: 8px;
}
.btn-ctrl {
  font-family: var(--mono); font-size: .68rem; letter-spacing: .06em;
  text-transform: uppercase;
  border: 1px solid var(--border); background: var(--surface);
  color: var(--text-dim); padding: 6px 14px; border-radius: 7px;
  cursor: pointer; display: inline-flex; align-items: center; gap: 6px;
  transition: color .15s, border-color .15s;
}
.btn-ctrl:hover { color: var(--accent-mid); border-color: var(--accent-mid); }
.btn-ctrl svg { width: 12px; height: 12px; transition: transform .2s; }

/* ── Blog grid ── */
.blog-grid {
  display: grid;
  gap: 14px;
  /* columns set inline */
}

/* ── Blog card ── */
.blog-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; overflow: hidden;
  transition: border-color .2s, transform .2s, box-shadow .2s;
}
.blog-card:hover {
  border-color: var(--accent-mid);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,.08);
}

.blog-card-header {
  padding: 18px 20px 0;
  cursor: pointer; user-select: none;
  display: flex; flex-direction: column; gap: 8px;
}
.blog-card-top {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 10px;
}
.blog-card-title {
  font-family: var(--serif); font-size: 1.05rem; font-weight: 400;
  color: var(--text); line-height: 1.35; flex: 1;
}
.blog-card-toggle {
  width: 26px; height: 26px; border-radius: 6px; flex-shrink: 0;
  background: var(--bg2); border: 1px solid var(--border);
  color: var(--text-dim); display: flex; align-items: center; justify-content: center;
  transition: background .15s, color .15s, transform .25s;
}
.blog-card-toggle svg { width: 13px; height: 13px; }
.blog-card.is-collapsed .blog-card-toggle { transform: rotate(-90deg); }

.blog-card-meta {
  display: flex; flex-wrap: wrap; align-items: center; gap: 8px;
  padding-bottom: 14px;
}
.blog-date {
  font-family: var(--mono); font-size: .68rem; color: var(--text-dim);
  letter-spacing: .04em;
}
.blog-tag {
  font-family: var(--mono); font-size: .62rem; letter-spacing: .05em;
  text-transform: uppercase;
  padding: 2px 8px; border-radius: 100px;
  background: var(--accent-light); color: var(--accent);
  border: 1px solid color-mix(in srgb, var(--accent) 20%, transparent);
}

/* ── Collapsible body ── */
.blog-card-body {
  overflow: hidden; max-height: 500px;
  transition: max-height .35s ease, opacity .25s ease, padding .25s ease;
  opacity: 1;
  border-top: 1px solid var(--border);
  padding: 16px 20px 20px;
}
.blog-card.is-collapsed .blog-card-body {
  max-height: 0; opacity: 0; padding-top: 0; padding-bottom: 0;
  border-top-color: transparent;
}
.blog-card-desc {
  font-size: .88rem; color: var(--text-muted); line-height: 1.75;
  margin-bottom: 14px;
}
.blog-read-link {
  font-family: var(--mono); font-size: .7rem; letter-spacing: .05em;
  color: var(--accent); text-decoration: none;
  display: inline-flex; align-items: center; gap: 6px;
  border-bottom: 1px solid transparent; transition: border-color .15s;
}
.blog-read-link:hover { border-color: var(--accent); }
.blog-read-link svg { width: 11px; height: 11px; }

@media (max-width: 720px) {
  .blog-grid { grid-template-columns: 1fr 1fr !important; }
}
@media (max-width: 480px) {
  .blog-grid { grid-template-columns: 1fr !important; }
}
"""

BLOG_JS = """
<script>
(function() {
  // ── Per-card toggle ──
  document.querySelectorAll('.blog-card-header').forEach(function(header) {
    header.addEventListener('click', function() {
      var card = header.closest('.blog-card');
      card.classList.toggle('is-collapsed');
      syncCtrlBtn();
    });
  });

  // ── Collapse-all / Expand-all ──
  var ctrlBtn = document.getElementById('btn-collapse-all');
  if (ctrlBtn) {
    ctrlBtn.addEventListener('click', function() {
      var cards       = document.querySelectorAll('.blog-card');
      var allCollapsed = Array.from(cards).every(function(c) { return c.classList.contains('is-collapsed'); });
      cards.forEach(function(c) {
        if (allCollapsed) c.classList.remove('is-collapsed');
        else              c.classList.add('is-collapsed');
      });
      syncCtrlBtn();
    });
  }

  function syncCtrlBtn() {
    var ctrlBtn = document.getElementById('btn-collapse-all');
    if (!ctrlBtn) return;
    var cards        = document.querySelectorAll('.blog-card');
    var allCollapsed = Array.from(cards).every(function(c) { return c.classList.contains('is-collapsed'); });
    ctrlBtn.querySelector('.ctrl-label').textContent = allCollapsed ? 'Expand All' : 'Collapse All';
    var icon = ctrlBtn.querySelector('svg');
    if (icon) icon.style.transform = allCollapsed ? 'rotate(180deg)' : '';
  }

  syncCtrlBtn();
})();
</script>
"""


def _format_date(d: str) -> str:
    """Turn 2024-11-10 → Nov 10, 2024"""
    try:
        from datetime import datetime
        return datetime.strptime(d, "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return d


def build_blog(cfg: dict, photo_cfg: dict, blog_cfg: dict) -> str:
    from site_builder.styles import build_css_vars, SHARED_CSS_TEMPLATE, HTML_HEAD_TEMPLATE
    from site_builder.nav import nav_html, footer_html, NAV_CSS, NAV_JS

    site  = cfg["site"]
    theme = cfg["theme"]
    bl    = blog_cfg.get("blog", {})
    posts = bl.get("posts", [])
    cols  = bl.get("grid_columns", 4)
    show_controls = bl.get("show_collapse_controls", True)

    shared_css = SHARED_CSS_TEMPLATE.format(css_vars=build_css_vars(theme))

    # Search index
    _img_icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>'
    _doc_icon  = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>'
    search_items = []
    for img in photo_cfg.get("photography", {}).get("images", []):
        cats = img.get("category", [])
        if isinstance(cats, str): cats = [cats]
        search_items.append({
            "title": img.get("alt", "Photo"),
            "href":  "photography.html",
            "tags":  cats,
            "meta":  img.get("location", "") + (" · " + str(img.get("year","")) if img.get("year") else ""),
            "icon":  _img_icon,
        })
    for post in posts:
        search_items.append({
            "title": post.get("title", "Post"),
            "href":  post.get("github_url", "blog.html"),
            "tags":  post.get("tags", []),
            "meta":  post.get("date", ""),
            "icon":  _doc_icon,
        })
    search_json = json.dumps(search_items, ensure_ascii=False)

    # Toolbar
    chevrons_svg = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">'
        '<polyline points="17 11 12 6 7 11"/>'
        '<polyline points="17 18 12 13 7 18"/></svg>'
    )
    toolbar_html = ""
    if show_controls:
        toolbar_html = f"""
  <div class="blog-toolbar">
    <button id="btn-collapse-all" class="btn-ctrl">
      {chevrons_svg}<span class="ctrl-label">Collapse All</span>
    </button>
  </div>"""

    # External link icon
    ext_svg = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
        '<path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>'
        '<polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>'
    )
    chevron_svg = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
        '<polyline points="6 9 12 15 18 9"/></svg>'
    )

    # Post cards
    cards_html = ""
    for post in posts:
        title      = esc(post.get("title", ""))
        desc       = esc(post.get("description", "").strip())
        date_raw   = post.get("date", "")
        date_fmt   = esc(_format_date(date_raw))
        github_url = esc(post.get("github_url", "#"))
        collapsed  = post.get("collapsed", False)
        tags       = post.get("tags", [])
        state_cls  = " is-collapsed" if collapsed else ""

        tags_html = "".join(f'<span class="blog-tag">{esc(t)}</span>' for t in tags)

        cards_html += f"""
    <div class="blog-card{state_cls}">
      <div class="blog-card-header">
        <div class="blog-card-top">
          <h2 class="blog-card-title">{title}</h2>
          <span class="blog-card-toggle">{chevron_svg}</span>
        </div>
        <div class="blog-card-meta">
          <span class="blog-date">{date_fmt}</span>
          {tags_html}
        </div>
      </div>
      <div class="blog-card-body">
        <p class="blog-card-desc">{desc}</p>
        <a class="blog-read-link" href="{github_url}" target="_blank" rel="noopener">
          {ext_svg} Read on GitHub →
        </a>
      </div>
    </div>"""

    return HTML_HEAD_TEMPLATE.format(
        title=esc(bl.get("page_title", "Blog")) + " — " + esc(site["title"]),
        description=esc(bl.get("intro", "")),
        default_mode=theme.get("default_mode", "light"),
        shared_css=shared_css,
        page_css=NAV_CSS + BLOG_CSS,
    ) + f"""
{nav_html(cfg, "blog")}

<main class="blog-page">
  <div class="page-eyebrow">{esc(bl.get('eyebrow', 'Written Notes'))}</div>
  <h1 class="page-title">{esc(bl.get('page_title', 'Blog'))}</h1>
  <p class="page-intro">{esc(bl.get('intro', '').strip())}</p>

  {toolbar_html}

  <div class="blog-grid" style="grid-template-columns: repeat({cols}, 1fr);">
    {cards_html}
  </div>
</main>

{footer_html(cfg)}

<script>window.SEARCH_INDEX = {search_json};</script>
{NAV_JS}
{BLOG_JS}
</body>
</html>
"""

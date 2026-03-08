"""
site_builder/pages/photo_page.py
==================================
Builds photography.html — image grid with tag filter, lightbox, and search.
"""
from __future__ import annotations
import html as _html
import json


def esc(s: str) -> str:
    return _html.escape(str(s), quote=True)


PHOTO_CSS = """
/* ── Photography page ── */
.photo-page { padding: 44px 18px 60px; max-width: var(--max); margin: 0 auto; animation: fade-up .5s ease both; }

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

/* ── Controls row: tags + grid switcher ── */
.photo-controls {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 10px; margin-bottom: 20px;
}

/* ── Tag filter bar ── */
.tag-bar {
  display: flex; flex-wrap: wrap; gap: 7px; align-items: center;
}
.tag-btn {
  font-family: var(--mono); font-size: .68rem; letter-spacing: .06em;
  text-transform: uppercase;
  border: 1px solid var(--border); background: var(--surface);
  color: var(--text-dim); padding: 5px 13px; border-radius: 100px;
  cursor: pointer; transition: color .15s, border-color .15s, background .15s;
}
.tag-btn:hover  { color: var(--accent-mid); border-color: var(--accent-mid); }
.tag-btn.active { background: var(--accent); border-color: var(--accent); color: #fff; }

/* ── Grid column switcher ── */
.grid-switcher {
  display: flex; align-items: center; gap: 4px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; padding: 3px;
  flex-shrink: 0;
}
.grid-btn {
  font-family: var(--mono); font-size: .68rem; letter-spacing: .04em;
  color: var(--text-dim); background: none; border: none;
  padding: 5px 11px; border-radius: 5px; cursor: pointer;
  transition: color .15s, background .15s;
  display: flex; align-items: center; gap: 5px;
}
.grid-btn:hover { color: var(--text); background: var(--bg2); }
.grid-btn.active { background: var(--accent); color: #fff; }
.grid-btn svg { width: 13px; height: 13px; }

/* ── Photo grid ── */
.photo-grid {
  display: grid;
  gap: 3px;
  transition: grid-template-columns .2s ease;
}
.photo-item {
  position: relative; overflow: hidden;
  aspect-ratio: 3/2; background: var(--bg2);
  cursor: pointer;
}
.photo-item img {
  width: 100%; height: 100%; object-fit: cover;
  display: block; transition: transform .45s ease;
}
.photo-item:hover img { transform: scale(1.05); }
.photo-item-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,.6) 0%, transparent 55%);
  opacity: 0; transition: opacity .3s ease;
  display: flex; flex-direction: column;
  justify-content: flex-end; padding: 14px;
}
.photo-item:hover .photo-item-overlay { opacity: 1; }
.photo-item-caption {
  font-size: .76rem; color: rgba(255,255,255,.92); line-height: 1.4;
}
.photo-item-meta {
  font-family: var(--mono); font-size: .64rem;
  color: rgba(255,255,255,.6); margin-top: 3px;
}
.photo-item.hidden { display: none; }

/* ── Empty state ── */
.photo-empty {
  grid-column: 1/-1; padding: 60px 0;
  text-align: center; color: var(--text-dim);
  font-size: .9rem;
}

/* ── Lightbox ── */
.lightbox {
  display: none; position: fixed; inset: 0; z-index: 300;
  background: rgba(0,0,0,.92); backdrop-filter: blur(8px);
  align-items: center; justify-content: center;
  padding: 20px;
}
.lightbox.is-open { display: flex; animation: fade-in .18s ease; }
.lightbox-inner {
  position: relative; max-width: min(1100px, 95vw); max-height: 90vh;
  animation: scale-in .2s ease;
}
.lightbox-img {
  max-width: 100%; max-height: 80vh;
  object-fit: contain; border-radius: 4px; display: block;
}
.lightbox-caption {
  margin-top: 14px; font-size: .88rem; color: rgba(255,255,255,.8);
  text-align: center; line-height: 1.5;
}
.lightbox-meta {
  font-family: var(--mono); font-size: .72rem;
  color: rgba(255,255,255,.45); text-align: center; margin-top: 4px;
}
.lightbox-close {
  position: absolute; top: -40px; right: 0;
  width: 34px; height: 34px; border-radius: 50%;
  background: rgba(255,255,255,.12); border: none; cursor: pointer;
  color: #fff; display: flex; align-items: center; justify-content: center;
  transition: background .15s;
}
.lightbox-close:hover { background: rgba(255,255,255,.22); }
.lightbox-prev, .lightbox-next {
  position: fixed; top: 50%; transform: translateY(-50%);
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.15);
  cursor: pointer; color: #fff;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s; font-size: 1.2rem;
}
.lightbox-prev { left: 20px; }
.lightbox-next { right: 20px; }
.lightbox-prev:hover, .lightbox-next:hover { background: rgba(255,255,255,.2); }

@media (max-width: 600px) {
  .photo-grid { gap: 2px; }
  .lightbox-prev { left: 6px; }
  .lightbox-next { right: 6px; }
}
"""

PHOTO_JS = """
<script>
(function() {
  // ── Grid column switcher ──
  var grid     = document.getElementById('photo-grid');
  var gridBtns = document.querySelectorAll('.grid-btn');
  gridBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
      gridBtns.forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
      var cols = btn.getAttribute('data-cols');
      if (grid) grid.style.gridTemplateColumns = 'repeat(' + cols + ', 1fr)';
    });
  });

  // ── Tag filter ──
  var tagBtns = document.querySelectorAll('.tag-btn');
  var items   = document.querySelectorAll('.photo-item');
  var emptyEl = document.getElementById('photo-empty');

  tagBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
      tagBtns.forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
      var tag = btn.getAttribute('data-tag');
      var visible = 0;
      items.forEach(function(item) {
        var cats = (item.getAttribute('data-cats') || '').split(',');
        var show = tag === 'all' || cats.indexOf(tag) > -1;
        item.classList.toggle('hidden', !show);
        if (show) visible++;
      });
      if (emptyEl) emptyEl.style.display = visible === 0 ? 'block' : 'none';
    });
  });

  // ── Lightbox ──
  var lb       = document.getElementById('lightbox');
  var lbImg    = document.getElementById('lb-img');
  var lbCap    = document.getElementById('lb-caption');
  var lbMeta   = document.getElementById('lb-meta');
  var lbClose  = document.getElementById('lb-close');
  var lbPrev   = document.getElementById('lb-prev');
  var lbNext   = document.getElementById('lb-next');
  if (!lb) return;

  var visibleItems = function() {
    return Array.from(items).filter(function(i) { return !i.classList.contains('hidden'); });
  };
  var currentIdx = 0;

  function openAt(idx) {
    var vi = visibleItems();
    if (!vi.length) return;
    currentIdx = (idx + vi.length) % vi.length;
    var item = vi[currentIdx];
    lbImg.src = item.getAttribute('data-src') || '';
    lbImg.alt = item.getAttribute('data-alt') || '';
    lbCap.textContent  = item.getAttribute('data-alt')  || '';
    lbMeta.textContent = item.getAttribute('data-meta') || '';
    lb.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }
  function closeLb() {
    lb.classList.remove('is-open');
    document.body.style.overflow = '';
    lbImg.src = '';
  }

  items.forEach(function(item, i) {
    item.addEventListener('click', function() {
      var vi = visibleItems();
      openAt(vi.indexOf(item));
    });
  });

  if (lbClose) lbClose.addEventListener('click', closeLb);
  lb.addEventListener('click', function(e) { if (e.target === lb) closeLb(); });
  if (lbPrev) lbPrev.addEventListener('click', function() { openAt(currentIdx - 1); });
  if (lbNext) lbNext.addEventListener('click', function() { openAt(currentIdx + 1); });

  document.addEventListener('keydown', function(e) {
    if (!lb.classList.contains('is-open')) return;
    if (e.key === 'Escape')     closeLb();
    if (e.key === 'ArrowLeft')  openAt(currentIdx - 1);
    if (e.key === 'ArrowRight') openAt(currentIdx + 1);
  });
})();
</script>
"""


def build_photography(cfg: dict, photo_cfg: dict, blog_cfg: dict) -> str:
    from site_builder.styles import build_css_vars, SHARED_CSS_TEMPLATE, HTML_HEAD_TEMPLATE
    from site_builder.nav import nav_html, footer_html, NAV_CSS, NAV_JS

    site      = cfg["site"]
    theme     = cfg["theme"]
    ph        = photo_cfg.get("photography", {})
    images    = ph.get("images", [])
    categories = ph.get("categories", ["all"])
    cols      = ph.get("grid_columns", 4)

    shared_css = SHARED_CSS_TEMPLATE.format(css_vars=build_css_vars(theme))

    # Build search index
    _img_icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>'
    _doc_icon  = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>'
    search_items = []
    for img in images:
        cats = img.get("category", [])
        if isinstance(cats, str): cats = [cats]
        search_items.append({
            "title": img.get("alt", "Photo"),
            "href":  "photography.html",
            "tags":  cats,
            "meta":  img.get("location", "") + (" · " + str(img.get("year","")) if img.get("year") else ""),
            "icon":  _img_icon,
        })
    for post in blog_cfg.get("blog", {}).get("posts", []):
        search_items.append({
            "title": post.get("title", "Post"),
            "href":  post.get("github_url", "blog.html"),
            "tags":  post.get("tags", []),
            "meta":  post.get("date", ""),
            "icon":  _doc_icon,
        })
    search_json = json.dumps(search_items, ensure_ascii=False)

    # Grid switcher SVG icons
    def _grid_icon(n):
        # Draw n×2 mini grid of rectangles
        rects = ""
        w, h, gap = 3.5, 3, 1
        cols_n = n
        total_w = cols_n * w + (cols_n - 1) * gap
        offset_x = (14 - total_w) / 2
        for row in range(2):
            for col in range(cols_n):
                x = offset_x + col * (w + gap)
                y = 1 + row * (h + gap)
                rects += f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx=".5"/>'
        return f'<svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">{rects}</svg>'

    # Tag filter bar
    tag_html = ""
    for cat in categories:
        active = " active" if cat == "all" else ""
        tag_html += f'<button class="tag-btn{active}" data-tag="{esc(cat)}">{esc(cat)}</button>\n'

    # Grid switcher — default col from config, options always 3/4/6
    default_cols = cols
    switcher_html = '<div class="grid-switcher">'
    for n in [3, 4, 6]:
        active = " active" if n == default_cols else ""
        switcher_html += (
            f'<button class="grid-btn{active}" data-cols="{n}" aria-label="{n} columns">'
            f'{_grid_icon(n)} {n}'
            f'</button>'
        )
    switcher_html += '</div>'

    controls_html = f'<div class="photo-controls"><div class="tag-bar">{tag_html}</div>{switcher_html}</div>'

    # Photo grid items
    grid_items = ""
    for img in images:
        src  = esc(img.get("src", ""))
        alt  = esc(img.get("alt", ""))
        loc  = img.get("location", "")
        yr   = str(img.get("year", ""))
        meta = (loc + (" · " + yr if yr else "")).strip(" · ")
        cats = img.get("category", [])
        if isinstance(cats, str): cats = [cats]
        cats_str = esc(",".join(cats))
        grid_items += f"""
    <div class="photo-item" data-cats="{cats_str}" data-src="{src}" data-alt="{alt}" data-meta="{esc(meta)}" tabindex="0" role="button" aria-label="{alt}">
      <img src="{src}" alt="{alt}" loading="lazy">
      <div class="photo-item-overlay">
        <div class="photo-item-caption">{alt}</div>
        <div class="photo-item-meta">{esc(meta)}</div>
      </div>
    </div>"""

    close_svg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'

    return HTML_HEAD_TEMPLATE.format(
        title=esc(ph.get("page_title", "Photography")) + " — " + esc(site["title"]),
        description=esc(ph.get("intro", "")),
        default_mode=theme.get("default_mode", "light"),
        shared_css=shared_css,
        page_css=NAV_CSS + PHOTO_CSS,
    ) + f"""
{nav_html(cfg, "photography")}

<main class="photo-page">
  <div class="page-eyebrow">{esc(ph.get('eyebrow', 'Visual Journal'))}</div>
  <h1 class="page-title">{esc(ph.get('page_title', 'Photography'))}</h1>
  <p class="page-intro">{esc(ph.get('intro', '').strip())}</p>

  {controls_html}

  <div class="photo-grid" id="photo-grid" style="grid-template-columns: repeat({cols}, 1fr);">
    {grid_items}
    <div class="photo-empty" id="photo-empty" style="display:none">No photos in this category yet.</div>
  </div>
</main>

<!-- Lightbox -->
<div class="lightbox" id="lightbox">
  <div class="lightbox-inner">
    <button class="lightbox-close" id="lb-close" aria-label="Close">{close_svg}</button>
    <img class="lightbox-img" id="lb-img" src="" alt="">
    <div class="lightbox-caption" id="lb-caption"></div>
    <div class="lightbox-meta"    id="lb-meta"></div>
  </div>
  <button class="lightbox-prev" id="lb-prev" aria-label="Previous">&#8592;</button>
  <button class="lightbox-next" id="lb-next" aria-label="Next">&#8594;</button>
</div>

{footer_html(cfg)}

<script>window.SEARCH_INDEX = {search_json};</script>
{NAV_JS}
{PHOTO_JS}
</body>
</html>
"""

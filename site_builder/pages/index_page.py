"""
site_builder/pages/index_page.py
==================================
Builds index.html — the landing/home page.

Hero is a two-column layout:
  left  — title, tagline, description, CTA buttons
  right — photo slideshow (controlled via main.yaml > hero_slideshow)
"""
from __future__ import annotations
import html as _html
import json


def esc(s: str) -> str:
    return _html.escape(str(s), quote=True)


INDEX_CSS = """
/* ── Hero ── */
.hero {
  min-height: calc(100vh - var(--nav-h));
  display: grid;
  grid-template-columns: 1fr 980px;
  gap: 0;
  align-items: center;
  padding: 0 28px 0 28px;
  position: relative; overflow: hidden;
}
.hero::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse 55% 70% at 20% 50%, var(--accent-light) 0%, transparent 65%);
  opacity: .55; pointer-events: none;
}
.hero-left {
  position: relative; z-index: 1;
  padding: 60px 48px 60px 0;
}
.hero-eyebrow {
  font-family: var(--mono); font-size: .7rem; letter-spacing: .18em;
  text-transform: uppercase; color: var(--accent-mid);
  margin-bottom: 20px; display: flex; align-items: center; gap: 12px;
  animation: fade-up .5s ease both;
}
.hero-eyebrow::before {
  content: ''; display: block; width: 32px; height: 1px; background: var(--accent-mid);
}
.hero-title {
  font-family: var(--serif); font-size: clamp(2.4rem, 5vw, 4.2rem);
  font-weight: 400; color: var(--text);
  line-height: 1.1; letter-spacing: -.02em;
  animation: fade-up .55s .08s ease both;
}
.hero-title em { font-style: italic; color: var(--accent-mid); }
.hero-desc {
  font-size: clamp(.88rem, 1.4vw, 1rem);
  color: var(--text-muted); max-width: 440px;
  line-height: 1.85; margin-top: 20px;
  animation: fade-up .55s .16s ease both;
}
.hero-actions {
  display: flex; gap: 12px; flex-wrap: wrap; margin-top: 32px;
  animation: fade-up .55s .24s ease both;
}
.btn-primary {
  font-family: var(--mono); font-size: .75rem; letter-spacing: .06em;
  text-transform: uppercase; text-decoration: none;
  background: var(--accent); color: #fff;
  padding: 11px 24px; border-radius: 8px;
  transition: opacity .15s, transform .15s;
  display: inline-block;
}
.btn-primary:hover { opacity: .88; transform: translateY(-1px); }
.btn-ghost {
  font-family: var(--mono); font-size: .75rem; letter-spacing: .06em;
  text-transform: uppercase; text-decoration: none;
  border: 1px solid var(--border); color: var(--text-muted);
  padding: 11px 24px; border-radius: 8px;
  transition: color .15s, border-color .15s, transform .15s;
  display: inline-block;
}
.btn-ghost:hover { color: var(--accent); border-color: var(--accent-mid); transform: translateY(-1px); }

/* ── Hero slideshow ── */
.hero-slideshow-wrap {
  position: relative; height: calc(100vh - var(--nav-h));
  display: flex; align-items: center; justify-content: center;
  padding: 32px 0 32px 16px;
}
.hero-slideshow {
  position: relative;
  width: 100%; max-width: 780px;
  height: min(380px, 70vh);
  border-radius: 16px; overflow: hidden;
  box-shadow: 0 32px 80px rgba(0,0,0,.18), 0 8px 24px rgba(0,0,0,.10);
  flex-shrink: 0;
  animation: fade-up .6s .3s ease both;
}
.hero-slide {
  position: absolute; inset: 0;
  opacity: 0;
  transition: opacity .9s ease;
}
.hero-slide.active { opacity: 1; }
.hero-slide img {
  width: 100%; height: 100%; object-fit: cover; display: block;
}
.hero-slide-caption {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 32px 18px 18px;
  background: linear-gradient(to top, rgba(0,0,0,.6) 0%, transparent 100%);
  font-size: .75rem; color: rgba(255,255,255,.8);
  font-family: var(--sans);
  opacity: 0; transition: opacity .3s ease;
}
.hero-slideshow:hover .hero-slide-caption { opacity: 1; }

/* Dot indicators */
.hero-slide-dots {
  position: absolute; bottom: 14px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 5px; z-index: 2;
}
.hero-slide-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: rgba(255,255,255,.35);
  transition: background .3s, transform .3s;
  cursor: pointer; border: none; padding: 0;
}
.hero-slide-dot.active {
  background: rgba(255,255,255,.9);
  transform: scale(1.3);
}

/* Corner accent mark */
.hero-slideshow::after {
  content: '';
  position: absolute; top: -1px; right: -1px;
  width: 60px; height: 60px;
  background: var(--bg);
  clip-path: polygon(100% 0, 0 0, 100% 100%);
  border-radius: 0 16px 0 0;
  opacity: .6; pointer-events: none;
}

/* ── Featured strip ── */
.featured {
  padding: 60px 28px;
  border-top: 1px solid var(--border);
}
.section-label {
  font-family: var(--mono); font-size: .68rem; letter-spacing: .16em;
  text-transform: uppercase; color: var(--text-dim);
  margin-bottom: 28px; display: flex; align-items: center; gap: 12px;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: var(--border); }

.featured-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 3px;
}
.featured-item {
  aspect-ratio: 4/3; overflow: hidden; position: relative;
  background: var(--bg2);
}
.featured-item img {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform .5s ease;
  display: block;
}
.featured-item:hover img { transform: scale(1.04); }
.featured-item-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,.55) 0%, transparent 50%);
  opacity: 0; transition: opacity .3s ease;
  display: flex; align-items: flex-end; padding: 16px;
}
.featured-item:hover .featured-item-overlay { opacity: 1; }
.featured-item-caption {
  font-size: .78rem; color: rgba(255,255,255,.9);
  font-family: var(--sans);
}

/* ── About strip ── */
.about-strip {
  padding: 60px 28px;
  border-top: 1px solid var(--border);
  display: grid; grid-template-columns: 1fr 1fr; gap: 60px;
  align-items: center;
}
.about-text h2 {
  font-family: var(--serif); font-size: 1.8rem; font-weight: 400;
  color: var(--text); margin-bottom: 16px; line-height: 1.25;
}
.about-text h2 em { font-style: italic; color: var(--accent-mid); }
.about-text p {
  font-size: .92rem; color: var(--text-muted); line-height: 1.85; margin-bottom: 10px;
}
.about-stats {
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
}
.stat-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 10px; padding: 20px;
}
.stat-num {
  font-family: var(--serif); font-size: 2rem; font-weight: 400;
  color: var(--accent); display: block; margin-bottom: 4px;
}
.stat-label { font-size: .78rem; color: var(--text-dim); font-family: var(--mono); letter-spacing: .05em; }

@media (max-width: 1024px) {
  .hero { grid-template-columns: 1fr 480px; }
  .hero-slideshow { max-width: 420px; }
}
@media (max-width: 820px) {
  .hero {
    grid-template-columns: 1fr;
    min-height: auto;
    padding-top: 48px; padding-bottom: 0;
  }
  .hero-left { padding: 0 0 32px; }
  .hero-slideshow-wrap {
    height: 300px; padding: 0 0 48px;
    justify-content: flex-start;
  }
  .hero-slideshow { max-width: 100%; height: 260px; border-radius: 12px; }
  .about-strip { grid-template-columns: 1fr; gap: 32px; }
  .featured-grid { grid-template-columns: 1fr 1fr; }
  .featured-grid .featured-item:last-child { display: none; }
}
@media (max-width: 560px) {
  .hero { padding: 36px 18px 0; }
  .featured { padding: 40px 18px; }
  .about-strip { padding: 40px 18px; }
  .featured-grid { grid-template-columns: 1fr; }
  .featured-grid .featured-item:last-child { display: block; }
}
"""

SLIDESHOW_JS = """
<script>
(function() {
  var slides   = document.querySelectorAll('.hero-slide');
  var dots     = document.querySelectorAll('.hero-slide-dot');
  var interval = parseInt(document.getElementById('hero-slideshow')
                          ? document.getElementById('hero-slideshow').getAttribute('data-interval') : '3500', 10) || 3500;
  if (!slides.length) return;

  var current = 0;

  function goTo(n) {
    slides[current].classList.remove('active');
    dots[current] && dots[current].classList.remove('active');
    current = (n + slides.length) % slides.length;
    slides[current].classList.add('active');
    dots[current] && dots[current].classList.add('active');
  }

  // Dot clicks
  dots.forEach(function(dot, i) {
    dot.addEventListener('click', function() { goTo(i); resetTimer(); });
  });

  // Auto-advance
  var timer = setInterval(function() { goTo(current + 1); }, interval);
  function resetTimer() { clearInterval(timer); timer = setInterval(function() { goTo(current + 1); }, interval); }

  // Pause on hover
  var wrap = document.getElementById('hero-slideshow');
  if (wrap) {
    wrap.addEventListener('mouseenter', function() { clearInterval(timer); });
    wrap.addEventListener('mouseleave', function() { timer = setInterval(function() { goTo(current + 1); }, interval); });
  }
})();
</script>
"""


def build_index(cfg: dict, photo_cfg: dict, blog_cfg: dict) -> str:
    from site_builder.styles import build_css_vars, SHARED_CSS_TEMPLATE, HTML_HEAD_TEMPLATE
    from site_builder.nav import nav_html, footer_html, NAV_CSS, NAV_JS

    site      = cfg["site"]
    theme     = cfg["theme"]
    photos    = photo_cfg.get("photography", {}).get("images", [])
    posts     = blog_cfg.get("blog", {}).get("posts", [])
    slideshow = cfg.get("hero_slideshow", {})

    featured = [p for p in photos if p.get("src")][:3]
    shared_css = SHARED_CSS_TEMPLATE.format(css_vars=build_css_vars(theme))

    # ── Search index ──
    _img_icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>'
    _doc_icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>'
    search_items = []
    for p in photos:
        cats = p.get("category", [])
        if isinstance(cats, str): cats = [cats]
        search_items.append({
            "title": p.get("alt", "Photo"), "href": "photography.html",
            "tags": cats,
            "meta": p.get("location", "") + (" · " + str(p.get("year","")) if p.get("year") else ""),
            "icon": _img_icon,
        })
    for post in posts:
        search_items.append({
            "title": post.get("title", "Post"), "href": post.get("github_url", "blog.html"),
            "tags": post.get("tags", []), "meta": post.get("date", ""), "icon": _doc_icon,
        })
    search_json = json.dumps(search_items, ensure_ascii=False)

    # ── Featured photos ──
    featured_html = ""
    for img in featured:
        src = esc(img.get("src", "")); alt = esc(img.get("alt", ""))
        featured_html += f"""
      <div class="featured-item">
        <img src="{src}" alt="{alt}" loading="lazy">
        <div class="featured-item-overlay">
          <span class="featured-item-caption">{alt}</span>
        </div>
      </div>"""

    # ── Hero title ──
    title_words = site["title"].rsplit(" ", 1)
    hero_title = f'{esc(title_words[0])} <em>{esc(title_words[1])}</em>' if len(title_words) == 2 else esc(site["title"])

    # ── Stats ──
    tags_set = set()
    for p in photos:
        cats = p.get("category", [])
        if isinstance(cats, str): cats = [cats]
        tags_set.update(cats)

    # ── Slideshow HTML ──
    show_slideshow = slideshow.get("show", True)
    interval_ms    = int(slideshow.get("interval_ms", 3500))
    slide_images   = slideshow.get("images", [])

    if show_slideshow and slide_images:
        slides_html = ""
        dots_html   = ""
        for i, img in enumerate(slide_images):
            active = " active" if i == 0 else ""
            src    = esc(img.get("src", ""))
            alt    = esc(img.get("alt", ""))
            slides_html += f"""
        <div class="hero-slide{active}">
          <img src="{src}" alt="{alt}" loading="{('eager' if i < 2 else 'lazy')}">
          <div class="hero-slide-caption">{alt}</div>
        </div>"""
            dots_html += f'<button class="hero-slide-dot{active}" aria-label="Slide {i+1}"></button>'

        slideshow_section = f"""
  <div class="hero-slideshow-wrap">
    <div class="hero-slideshow" id="hero-slideshow" data-interval="{interval_ms}">
      {slides_html}
      <div class="hero-slide-dots">{dots_html}</div>
    </div>
  </div>"""
        slideshow_js = SLIDESHOW_JS
    else:
        slideshow_section = ""
        slideshow_js = ""

    return HTML_HEAD_TEMPLATE.format(
        title=esc(site["title"]) + " — Home",
        description=esc(site.get("description", "")),
        default_mode=theme.get("default_mode", "light"),
        shared_css=shared_css,
        page_css=NAV_CSS + INDEX_CSS,
    ) + f"""
{nav_html(cfg, "index")}

<main>
  <!-- Hero -->
  <section class="hero">
    <div class="hero-left">
      <div class="hero-eyebrow">{esc(site.get('tagline', ''))}</div>
      <h1 class="hero-title">{hero_title}</h1>
      <p class="hero-desc">{esc(site.get('description', ''))}</p>
      <div class="hero-actions">
        <a class="btn-primary" href="photography.html">View Photography</a>
        <a class="btn-ghost"   href="blog.html">Read the Blog</a>
      </div>
    </div>
    {slideshow_section}
  </section>

  <!-- Featured photos -->
  <section class="featured">
    <div class="section-label">Recent Work</div>
    <div class="featured-grid">{featured_html}
    </div>
  </section>

  <!-- About strip -->
  <section class="about-strip">
    <div class="about-text">
      <h2>Collecting <em>light</em><br>one frame at a time</h2>
      <p>{esc(site.get('description', ''))}</p>
      <p style="margin-top:20px">
        <a class="btn-ghost" href="photography.html">Explore the archive →</a>
      </p>
    </div>
    <div class="about-stats">
      <div class="stat-card">
        <span class="stat-num">{len(photos)}</span>
        <span class="stat-label">Photographs</span>
      </div>
      <div class="stat-card">
        <span class="stat-num">{len(posts)}</span>
        <span class="stat-label">Blog posts</span>
      </div>
      <div class="stat-card">
        <span class="stat-num">{len(tags_set)}</span>
        <span class="stat-label">Categories</span>
      </div>
      <div class="stat-card">
        <span class="stat-num">∞</span>
        <span class="stat-label">Rolls to shoot</span>
      </div>
    </div>
  </section>
</main>

{footer_html(cfg)}

<script>window.SEARCH_INDEX = {search_json};</script>
{NAV_JS}
{slideshow_js}
</body>
</html>
"""

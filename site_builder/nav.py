"""
site_builder/nav.py
====================
Shared navigation bar and footer, driven by main.yaml.
"""
from __future__ import annotations
import html as _html


def esc(s: str) -> str:
    return _html.escape(str(s), quote=True)


# SVG icons for social links
_SOCIAL_ICONS = {
    "github": (
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217'
        '.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11'
        '-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53'
        ' 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0'
        '-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564'
        ' 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027'
        '.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566'
        ' 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.02'
        ' 10.02 0 0 0 22 12.017C22 6.484 17.522 2 12 2z"/></svg>'
    ),
    "instagram": (
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'
        '<rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>'
        '<path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>'
        '<line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>'
    ),
    "twitter": (
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744'
        'l7.73-8.835L1.254 2.25H8.08l4.258 5.63zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>'
    ),
}

_SEARCH_SVG = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
)
_MOON_SVG = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'
)
_SUN_SVG = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<circle cx="12" cy="12" r="5"/>'
    '<line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>'
    '<line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>'
    '<line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>'
    '<line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'
)
_MENU_SVG = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>'
)
_CLOSE_SVG = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
)

NAV_CSS = """
/* ── Navigation ── */
.nav {
  position: sticky; top: 0; z-index: 100;
  height: var(--nav-h);
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex; align-items: center;
  padding: 0 28px;
  gap: 0;
  transition: var(--transition);
}
.nav-brand {
  font-family: var(--serif); font-size: 1.15rem; font-weight: 400;
  color: var(--text); text-decoration: none; letter-spacing: .01em;
  white-space: nowrap; margin-right: auto;
}
.nav-brand em { font-style: italic; color: var(--accent-mid); }
.nav-links {
  display: flex; align-items: center; gap: 2px; margin-right: 12px;
}
.nav-link {
  font-family: var(--sans); font-size: .82rem; font-weight: 400;
  color: var(--text-muted); text-decoration: none; letter-spacing: .04em;
  padding: 6px 14px; border-radius: 6px;
  transition: color .15s, background .15s;
}
.nav-link:hover  { color: var(--text); background: var(--bg2); }
.nav-link.active { color: var(--accent); font-weight: 500; }
.nav-actions { display: flex; align-items: center; gap: 4px; }
.nav-btn {
  width: 34px; height: 34px; border-radius: 7px;
  border: 1px solid transparent; background: none; cursor: pointer;
  color: var(--text-muted); display: flex; align-items: center; justify-content: center;
  transition: color .15s, background .15s, border-color .15s;
}
.nav-btn:hover { color: var(--text); background: var(--bg2); border-color: var(--border); }
.nav-hamburger { display: none; }

/* ── Search overlay ── */
.search-overlay {
  display: none; position: fixed; inset: 0; z-index: 200;
  background: rgba(0,0,0,.5); backdrop-filter: blur(4px);
  align-items: flex-start; justify-content: center;
  padding-top: 80px;
}
.search-overlay.is-open { display: flex; animation: fade-in .15s ease; }
.search-box {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 14px; width: min(600px, 92vw);
  box-shadow: 0 20px 60px rgba(0,0,0,.25);
  overflow: hidden; animation: scale-in .18s ease;
}
.search-input-wrap {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 18px; border-bottom: 1px solid var(--border);
}
.search-input-wrap svg { color: var(--text-dim); flex-shrink: 0; }
.search-input {
  flex: 1; background: none; border: none; outline: none;
  font-family: var(--sans); font-size: 1rem; color: var(--text);
}
.search-input::placeholder { color: var(--text-dim); }
.search-results { max-height: 360px; overflow-y: auto; padding: 8px; }
.search-result-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px; border-radius: 8px; cursor: pointer;
  text-decoration: none; color: var(--text);
  transition: background .12s;
}
.search-result-item:hover { background: var(--bg2); }
.search-result-icon { color: var(--text-dim); flex-shrink: 0; }
.search-result-title { font-size: .9rem; font-weight: 500; }
.search-result-meta  { font-size: .78rem; color: var(--text-muted); margin-top: 1px; }
.search-empty { padding: 28px 18px; text-align: center; color: var(--text-dim); font-size: .88rem; }
.search-hint  { padding: 8px 18px 12px; font-size: .75rem; color: var(--text-dim); }

/* ── Mobile nav drawer ── */
.nav-drawer {
  display: none; position: fixed; inset: 0; z-index: 150;
  background: var(--surface); flex-direction: column;
  padding: 20px 24px; gap: 6px;
  animation: fade-in .15s ease;
}
.nav-drawer.is-open { display: flex; }
.nav-drawer-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px;
}
.nav-drawer-link {
  font-family: var(--sans); font-size: 1.1rem;
  color: var(--text-muted); text-decoration: none;
  padding: 10px 4px; border-bottom: 1px solid var(--border);
  transition: color .15s;
}
.nav-drawer-link:hover, .nav-drawer-link.active { color: var(--accent); }

/* ── Footer ── */
.footer {
  border-top: 1px solid var(--border);
  padding: 32px 28px;
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 14px;
  font-size: .8rem; color: var(--text-dim);
  margin-top: 60px;
}
.footer-social { display: flex; gap: 8px; }
.footer-social a {
  width: 32px; height: 32px; border-radius: 7px;
  border: 1px solid var(--border); background: var(--surface);
  color: var(--text-muted); display: flex; align-items: center; justify-content: center;
  text-decoration: none; transition: color .15s, border-color .15s;
}
.footer-social a:hover { color: var(--accent); border-color: var(--accent-mid); }

@media (max-width: 720px) {
  .nav-links { display: none; }
  .nav-hamburger { display: flex; }
  .footer { flex-direction: column; align-items: flex-start; }
}
"""

NAV_JS = """
<script>
// ── Theme toggle ──
(function() {
  var html = document.documentElement;
  var btn  = document.getElementById('theme-btn');
  if (!btn) return;
  function sync() {
    var dark = html.getAttribute('data-theme') === 'dark';
    btn.innerHTML = dark
      ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'
      : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    btn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
  }
  btn.addEventListener('click', function() {
    var next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    sync();
  });
  var saved = localStorage.getItem('theme');
  if (saved) { html.setAttribute('data-theme', saved); }
  sync();
})();

// ── Search ──
(function() {
  var overlay = document.getElementById('search-overlay');
  var input   = document.getElementById('search-input');
  var results = document.getElementById('search-results');
  var openBtn = document.getElementById('search-btn');
  if (!overlay) return;

  function open() { overlay.classList.add('is-open'); setTimeout(function(){ input && input.focus(); }, 50); }
  function close() { overlay.classList.remove('is-open'); if(input) input.value=''; renderResults(''); }

  if (openBtn) openBtn.addEventListener('click', open);
  overlay.addEventListener('click', function(e) { if (e.target === overlay) close(); });
  document.addEventListener('keydown', function(e) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); open(); }
    if (e.key === 'Escape') close();
  });

  function renderResults(q) {
    if (!results) return;
    var items = (window.SEARCH_INDEX || []);
    var filtered = q.length < 2 ? [] : items.filter(function(it) {
      return (it.title + ' ' + (it.tags || []).join(' ') + ' ' + (it.meta || '')).toLowerCase().indexOf(q.toLowerCase()) > -1;
    });
    if (q.length < 2) {
      results.innerHTML = '<p class="search-empty">Start typing to search…</p>';
      return;
    }
    if (!filtered.length) {
      results.innerHTML = '<p class="search-empty">No results for <strong>' + q + '</strong></p>';
      return;
    }
    results.innerHTML = filtered.map(function(it) {
      return '<a class="search-result-item" href="' + it.href + '">'
        + '<span class="search-result-icon">' + (it.icon || '') + '</span>'
        + '<span><div class="search-result-title">' + it.title + '</div>'
        + '<div class="search-result-meta">' + (it.meta || '') + '</div></span></a>';
    }).join('');
  }

  if (input) input.addEventListener('input', function() { renderResults(this.value); });
  renderResults('');
})();

// ── Mobile drawer ──
(function() {
  var btn    = document.getElementById('hamburger-btn');
  var drawer = document.getElementById('nav-drawer');
  var close  = document.getElementById('drawer-close');
  if (!btn || !drawer) return;
  btn.addEventListener('click', function()   { drawer.classList.add('is-open'); });
  if (close) close.addEventListener('click', function() { drawer.classList.remove('is-open'); });
})();
</script>
"""


def nav_html(cfg: dict, active_page: str) -> str:
    site = cfg["site"]
    nav  = cfg.get("nav", [])

    links_html = ""
    for item in nav:
        label = esc(item["label"])
        href  = esc(item["href"])
        page_key = item["href"].replace(".html", "").replace("index", "home")
        active_class = " active" if page_key == active_page or item["href"] == active_page + ".html" else ""
        links_html += f'<a class="nav-link{active_class}" href="{href}">{label}</a>\n'

    drawer_links = ""
    for item in nav:
        label = esc(item["label"])
        href  = esc(item["href"])
        page_key = item["href"].replace(".html", "").replace("index", "home")
        active_class = " active" if page_key == active_page else ""
        drawer_links += f'<a class="nav-drawer-link{active_class}" href="{href}">{label}</a>\n'

    brand_title = esc(site["title"])
    # Split title at last word for italic accent
    words = site["title"].rsplit(" ", 1)
    if len(words) == 2:
        brand_html = f'{esc(words[0])} <em>{esc(words[1])}</em>'
    else:
        brand_html = brand_title

    return f"""
<nav class="nav">
  <a class="nav-brand" href="index.html">{brand_html}</a>
  <div class="nav-links">{links_html}</div>
  <div class="nav-actions">
    <button class="nav-btn" id="search-btn" aria-label="Search">{_SEARCH_SVG}</button>
    <button class="nav-btn" id="theme-btn" aria-label="Toggle theme">{_MOON_SVG}</button>
    <button class="nav-btn nav-hamburger" id="hamburger-btn" aria-label="Menu">{_MENU_SVG}</button>
  </div>
</nav>

<!-- Mobile drawer -->
<div class="nav-drawer" id="nav-drawer">
  <div class="nav-drawer-header">
    <a class="nav-brand" href="index.html">{brand_html}</a>
    <button class="nav-btn" id="drawer-close" aria-label="Close">{_CLOSE_SVG}</button>
  </div>
  {drawer_links}
</div>

<!-- Search overlay -->
<div class="search-overlay" id="search-overlay">
  <div class="search-box">
    <div class="search-input-wrap">
      {_SEARCH_SVG}
      <input class="search-input" id="search-input" type="text"
             placeholder="Search photos, posts, tags…" autocomplete="off">
    </div>
    <div class="search-results" id="search-results">
      <p class="search-empty">Start typing to search…</p>
    </div>
    <div class="search-hint">Press <kbd>Esc</kbd> to close · <kbd>⌘K</kbd> to open</div>
  </div>
</div>
"""


def footer_html(cfg: dict) -> str:
    footer = cfg.get("footer", {})
    note   = esc(footer.get("note", ""))
    social = footer.get("social", [])

    social_html = ""
    for s in social:
        icon = _SOCIAL_ICONS.get(s.get("icon", ""), "")
        social_html += f'<a href="{esc(s["href"])}" target="_blank" rel="noopener" aria-label="{esc(s["label"])}">{icon}</a>\n'

    return f"""
<footer class="footer">
  <span>{note}</span>
  <div class="footer-social">{social_html}</div>
</footer>
"""

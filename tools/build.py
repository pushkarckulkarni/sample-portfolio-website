#!/usr/bin/env python3
"""
================================================================================
SAMPLE PORTFOLIO — SITE BUILDER
================================================================================

WHAT THIS DOES
    Reads everything from  website/content/  and writes the .html files into
    website/ .  Nothing else. Your text lives in JSON, your photos live in
    folders, and this turns both into the website.

HOW TO USE IT
    python3 tools/build.py

WHAT YOU EDIT (never edit the .html files by hand — they get overwritten)
    website/content/site.json                      brand, contact, nav, home page
    website/content/about.json                     the About page
    website/content/news.json                      news, press, awards, books
    website/content/projects/<slug>/project.json   one project
    website/content/projects/<slug>/cover.jpg      its grid thumbnail
    website/content/projects/<slug>/hero.jpg       its banner
    website/content/projects/<slug>/gallery/*.jpg  its photo sequence

WHAT GETS GENERATED
    index.html · projects.html · about.html · news.html · press.html
    awards.html · books.html · contact.html · 404.html
    project-<slug>.html   (one per project folder)

ADDING A PROJECT
    1. Copy an existing folder in website/content/projects/ and rename it.
    2. Replace the images inside.
    3. Edit its project.json.
    4. Run this script.
    The grid, the nav, the prev/next links and the new page all update together.
    You never touch HTML.
================================================================================
"""

import os, json, glob, sys

HERE    = os.path.dirname(os.path.abspath(__file__))
ROOT    = os.path.normpath(os.path.join(HERE, ".."))
WEB     = os.path.join(ROOT, "website")
CONTENT = os.path.join(WEB, "content")

# Image dimensions must match the presets in image-prep/presets.json.
# They are written into width/height attributes, which is what keeps CLS at 0.
DIMS = {
    "hero":        (2400, 1350),
    "hero-mobile": (1200, 1500),
    "cover":       (1200,  900),
    "gallery":     (2000, 1333),
    "principal":   ( 900, 1125),
    "team":        ( 700,  700),
    "news":        (1000,  750),
}


# ------------------------------------------------------------------ helpers --

def load(name):
    p = os.path.join(CONTENT, name)
    if not os.path.exists(p):
        sys.exit(f"ERROR: missing {p}")
    with open(p, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            sys.exit(f"ERROR: {name} is not valid JSON — {e}\n"
                     f"       Line {e.lineno}. Usually a missing comma or a stray quote.")


def load_projects():
    """One folder per project. The folder IS the project."""
    out = []
    for pj in sorted(glob.glob(os.path.join(CONTENT, "projects", "*", "project.json"))):
        folder = os.path.dirname(pj)
        slug   = os.path.basename(folder)
        with open(pj, encoding="utf-8") as f:
            try:
                d = json.load(f)
            except json.JSONDecodeError as e:
                sys.exit(f"ERROR: {pj} is not valid JSON — {e} (line {e.lineno})")
        d["slug"]   = d.get("slug", slug)
        d["folder"] = slug
        d["_dir"]   = folder

        # Warn loudly about missing images rather than silently shipping a
        # broken page — a 404'd hero is very easy to miss when reviewing.
        for key in ("cover", "hero"):
            f_ = d.get(key)
            if f_ and not os.path.exists(os.path.join(folder, f_)):
                print(f"  ! WARNING  {slug}: {key} image not found -> {f_}")
        for g in d.get("gallery", []):
            if not os.path.exists(os.path.join(folder, g["file"])):
                print(f"  ! WARNING  {slug}: gallery image not found -> {g['file']}")
        out.append(d)

    out.sort(key=lambda p: p.get("order", 999))
    return out


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def img(src, kind, alt="", lazy=True, cls="", extra=""):
    w, h = DIMS[kind]
    parts = []
    if cls:
        parts.append(f'class="{cls}"')
    parts.append(f'src="{src}"')
    parts.append(f'alt="{esc(alt)}"')
    parts.append(f'width="{w}"')
    parts.append(f'height="{h}"')
    parts.append('loading="lazy"' if lazy else 'fetchpriority="high"')
    if extra:
        parts.append(extra)
    return "<img " + " ".join(parts) + ">"


# ------------------------------------------------------------------- chrome --

def head(S, title, desc, og_image="content/home/hero/01.jpg", preload=None):
    pre = f'\n<link rel="preload" as="image" href="{preload}" fetchpriority="high">' if preload else ""
    return f"""<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{S['domain']}/{og_image}">{pre}
<link rel="stylesheet" href="assets/css/tokens.css">
<link rel="stylesheet" href="assets/css/base.css">
<link rel="stylesheet" href="assets/css/components.css">
<link rel="stylesheet" href="assets/css/responsive.css">
<script>document.documentElement.className=document.documentElement.className.replace('no-js','js');</script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>"""


NEWS_TABS = [("news.html", "Highlights"), ("press.html", "Press"),
             ("awards.html", "Awards"), ("books.html", "Books")]


def cat_href(slug):
    return "projects.html" if slug == "all" else f"projects.html?cat={slug}"


def header(S, active, subnav="", h1=""):
    def li(name):
        return ' class="nav-primary__item is-active"' if name == active else ' class="nav-primary__item"'

    pdrop = "\n".join(f'            <li><a class="nav-drop__link" href="{cat_href(c["slug"])}">{esc(c["label"])}</a></li>'
                      for c in S["categories"])
    ndrop = "\n".join(f'            <li><a class="nav-drop__link" href="{h}">{l}</a></li>'
                      for h, l in NEWS_TABS)
    psub = "\n".join(f'      <a class="mobile-menu__sublink" href="{cat_href(c["slug"])}">{esc(c["label"])}</a>'
                     for c in S["categories"])
    nsub = "\n".join(f'      <a class="mobile-menu__sublink" href="{h}">{l}</a>' for h, l in NEWS_TABS)

    return f"""

<!-- ================= M-01 HEADER ================= -->
<header class="site-header">
  <div class="site-header__bar">
    <a class="site-logo" href="index.html">
      <span class="site-logo__mark">{esc(S['brand'])}</span>
      <span class="site-logo__sub">{esc(S['tagline'])}</span>
    </a>

    <nav class="nav-primary" aria-label="Primary">
      <ul class="nav-primary__list">
        <li{li('projects')}>
          <a class="nav-primary__link" href="projects.html">Projects</a>
          <ul class="nav-drop">
{pdrop}
          </ul>
        </li>
        <li{li('about')}><a class="nav-primary__link" href="about.html">About</a></li>
        <li{li('news')}>
          <a class="nav-primary__link" href="news.html">News</a>
          <ul class="nav-drop">
{ndrop}
          </ul>
        </li>
        <li{li('contact')}><a class="nav-primary__link" href="contact.html">Contact</a></li>
      </ul>
    </nav>

    <button class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-menu">
      <span class="nav-toggle__bar"></span><span class="nav-toggle__bar"></span><span class="nav-toggle__bar"></span>
    </button>
  </div>
{subnav}</header>

<!-- ================= M-03 MOBILE MENU ================= -->
<div class="mobile-menu" id="mobile-menu">
  <nav aria-label="Mobile">
    <a class="mobile-menu__link" href="projects.html">Projects</a>
    <div class="mobile-menu__sub">
{psub}
    </div>
    <a class="mobile-menu__link" href="about.html">About</a>
    <a class="mobile-menu__link" href="news.html">News</a>
    <div class="mobile-menu__sub">
{nsub}
    </div>
    <a class="mobile-menu__link" href="contact.html">Contact</a>
  </nav>
  <p class="mobile-menu__foot">{esc(S['email'])}<br>{esc(S['phone'])}</p>
</div>

<main id="main">{h1}"""


def sr_h1(t):
    return f'\n  <h1 class="u-sr-only">{esc(t)}</h1>'


def subnav_projects(S):
    items = "\n".join(
        f'      <li class="subnav__item"><a class="subnav__link{" is-active" if c["slug"]=="all" else ""}"'
        f' data-cat="{c["slug"]}" href="{cat_href(c["slug"])}">{esc(c["label"])}</a></li>'
        for c in S["categories"])
    return f'  <nav class="subnav" aria-label="Project categories" data-filter-bar>\n    <ul class="subnav__list">\n{items}\n    </ul>\n  </nav>\n'


def subnav_news(active):
    items = "\n".join(
        f'      <li class="subnav__item"><a class="subnav__link{" is-active" if h==active else ""}" href="{h}">{l}</a></li>'
        for h, l in NEWS_TABS)
    return f'  <nav class="subnav" aria-label="News sections">\n    <ul class="subnav__list">\n{items}\n    </ul>\n  </nav>\n'


def subnav_about():
    secs = [("firm", "The Firm"), ("philosophy", "Design Philosophy"),
            ("principals", "Principals"), ("team", "Team")]
    items = "\n".join(
        f'      <li class="subnav__item"><a class="subnav__link{" is-active" if i==0 else ""}" href="#{a}">{l}</a></li>'
        for i, (a, l) in enumerate(secs))
    return f'  <nav class="subnav" aria-label="About sections" data-spy>\n    <ul class="subnav__list">\n{items}\n    </ul>\n  </nav>\n'


def footer(S):
    social = "".join(f'<a href="{s["url"]}">{esc(s["label"])}</a>' for s in S["social"])
    return f"""
</main>

<!-- ================= M-12 FOOTER ================= -->
<footer class="site-footer">
  <div class="u-container">
    <div class="site-footer__row">
      <a href="mailto:{S['email']}">{esc(S['email'])}</a>
      <nav class="site-footer__social" aria-label="Social">{social}</nav>
      <p>&copy; {esc(S['brand'])} {S['copyrightYear']}</p>
    </div>
  </div>
</footer>

<button class="to-top" aria-label="Back to top">&uarr;</button>
<script src="assets/js/site.js" defer></script>
</body>
</html>
"""


TOP_PAD = 'style="padding-top:calc(var(--header-h-sub) + var(--sp-8))"'


# -------------------------------------------------------------------- cards --

def project_card(p, i, reveal=True):
    src = f"content/projects/{p['folder']}/{p.get('cover','cover.jpg')}"
    rv  = f' data-reveal data-reveal-delay="{i%3}"' if reveal else ""
    return f"""      <a class="card" href="project-{p['slug']}.html" data-cats="{p['category']}"{rv}>
        <div class="card__media">{img(src,'cover',p['title'],cls='card__img')}</div>
        <div class="card__body">
          <h3 class="card__title">{esc(p['title'])}</h3>
          <p class="card__meta">{esc(p['location'])}, {esc(p['year'])}</p>
        </div>
      </a>"""


def news_card(n, i):
    return f"""      <a class="news-card" href="{n.get('url','#')}" data-reveal data-reveal-delay="{i%3}">
        <div class="news-card__media">{img('content/news/'+n['photo'],'news','',cls='news-card__img')}</div>
        <p class="news-card__body">{n['text']}</p>
        <p class="news-card__date">{esc(n['date'])}</p>
      </a>"""


# -------------------------------------------------------------------- pages --

def page_home(S, P, N):
    heroes = sorted(glob.glob(os.path.join(CONTENT, "home", "hero", "*.jpg")))
    if not heroes:
        sys.exit("ERROR: no images in website/content/home/hero/")
    slides = []
    for i, h in enumerate(heroes):
        f = os.path.basename(h)
        slides.append(
            f'    <div class="hero__slide{" is-active" if i==0 else ""}" role="group" aria-label="{i+1} of {len(heroes)}">\n'
            f'      {img("content/home/hero/"+f,"hero",f"Featured project {i+1}",lazy=(i>0),cls="hero__img")}\n'
            f'    </div>')
    dots = "\n".join(f'      <button class="hero__dot{" is-active" if i==0 else ""}" role="tab" aria-label="Slide {i+1}"></button>'
                     for i in range(len(heroes)))

    featured = [p for p in P if p.get("featured")][:6] or P[:6]
    cards = "\n".join(project_card(p, i) for i, p in enumerate(featured))
    latest = "\n".join(news_card(n, i) for i, n in enumerate(N["highlights"][:3]))
    H = S["home"]

    return f"""
  <!-- ================= M-04 HERO SLIDER ================= -->
  <section class="hero" data-interval="{H['heroInterval']}" tabindex="-1" aria-roledescription="carousel" aria-label="Featured projects">
{chr(10).join(slides)}

    <div class="hero__scrim"></div>
    <button class="hero__nav hero__nav--prev" aria-label="Previous slide"></button>
    <button class="hero__nav hero__nav--next" aria-label="Next slide"></button>

    <div class="hero__caption">
      <h1 class="hero__title">{esc(H['heroCaption'])}</h1>
      <p class="hero__meta">{esc(H['heroCaptionMeta'])}</p>
    </div>

    <div class="hero__dots" role="tablist" aria-label="Slide navigation">
{dots}
    </div>

    <div class="hero__cue"><span class="hero__cue-line"></span>Scroll</div>
  </section>

  <!-- ================= SELECTED WORK ================= -->
  <section class="u-container u-section">
    <header class="about-section__head" data-reveal><h2 class="u-label">{esc(H['selectedWorkLabel'])}</h2></header>
    <div class="grid grid--dim">
{cards}
    </div>
    <div class="pager"><a class="pager__btn" href="projects.html">All Projects</a></div>
  </section>

  <!-- ================= PRACTICE ================= -->
  <section class="u-container u-container--prose u-section u-rule">
    <h2 class="u-label" data-reveal>{esc(H['practiceLabel'])}</h2>
    <p class="pd-intro" data-reveal data-reveal-delay="1">{esc(H['practiceText'])}</p>
    <div class="u-text-center"><a class="pager__btn" href="about.html">About the Studio</a></div>
  </section>

  <!-- ================= LATEST ================= -->
  <section class="u-container u-section u-rule">
    <header class="about-section__head" data-reveal><h2 class="u-label">{esc(H['latestLabel'])}</h2></header>
    <div class="grid">
{latest}
    </div>
  </section>
"""


def page_projects(S, P):
    cards = "\n".join(project_card(p, i) for i, p in enumerate(P))
    return f"""
  <section class="u-container u-section" {TOP_PAD}>
    <h2 class="u-sr-only">All Projects</h2>
    <div class="u-sr-only" role="status" data-filter-count aria-live="polite"></div>
    <div class="grid grid--dim" id="project-grid" data-filter-grid>
{cards}
    </div>
    <div class="pager">
      <button class="pager__btn" data-load-more="6" data-target="project-grid">Load More</button>
    </div>
  </section>
"""


def page_project(S, p, prev, nxt):
    d = f"content/projects/{p['folder']}"
    intro = "\n      ".join(f"<p>{esc(t)}</p>" for t in p.get("intro", []))

    # Look up the display label from site.json rather than title-casing the raw
    # slug. The slug ("residential") is the stable link to project.json and to
    # the nav/filter tabs; the label (e.g. "Architecture") is what a visitor
    # sees and is free to be renamed at any time in site.json alone.
    cat_label = next((c["label"] for c in S["categories"] if c["slug"] == p["category"]),
                     p["category"].title())

    # Build the image sequence, injecting the pull quote after N images.
    blocks, pair = [], []
    gal = p.get("gallery", [])
    quote_after = p.get("pullQuoteAfter", 0)

    def flush_pair():
        if not pair:
            return
        if len(pair) == 1:
            cap = pair[0][1]
            capline = f'\n    <figcaption class="figure__cap u-container">{esc(cap)}</figcaption>' if cap else ""
            blocks.append(f'  <figure class="figure figure--full" data-reveal>\n'
                          f'    {img(pair[0][0],"gallery",cap,cls="figure__img",extra="data-lightbox")}'
                          f'{capline}\n  </figure>')
        else:
            inner = "\n".join(
                f'      <figure class="figure" style="margin:0">{img(s,"gallery",c,cls="figure__img",extra="data-lightbox")}</figure>'
                for s, c in pair)
            blocks.append(f'  <div class="u-container">\n    <div class="figure-pair" data-reveal>\n{inner}\n    </div>\n  </div>')
        pair.clear()

    for i, g in enumerate(gal):
        src, cap = f"{d}/{g['file']}", g.get("caption", "")
        if g.get("layout") == "pair":
            pair.append((src, cap))
            if len(pair) == 2:
                flush_pair()
        else:
            flush_pair()
            capline = f'\n    <figcaption class="figure__cap u-container">{esc(cap)}</figcaption>' if cap else ""
            blocks.append(f'  <figure class="figure figure--full" data-reveal>\n'
                          f'    {img(src,"gallery",cap or p["title"],cls="figure__img",extra="data-lightbox")}'
                          f'{capline}\n  </figure>')
        if quote_after and i + 1 == quote_after and p.get("pullQuote"):
            flush_pair()
            blocks.append('  <div class="u-container">\n'
                          f'    <blockquote class="pullquote" data-reveal>{esc(p["pullQuote"])}</blockquote>\n'
                          '  </div>')
    flush_pair()

    credits = "\n".join(
        f'      <div><dt class="credits__key">{esc(k)}</dt><dd class="credits__val">{esc(v)}</dd></div>'
        for k, v in p.get("credits", {}).items())

    return f"""
  <!-- M-07a hero -->
  <section class="pd-hero">
    {img(f"{d}/{p.get('hero','hero.jpg')}", 'hero', p['title'], lazy=False, cls='pd-hero__img')}
  </section>

  <!-- M-07b title -->
  <div class="u-container">
    <header class="pd-head">
      <h1 class="pd-head__title">{esc(p['title'])}</h1>
      <p class="pd-head__meta">{esc(p['location'])}, {esc(p['year'])} &middot; {esc(cat_label)}</p>
    </header>
  </div>

  <!-- M-07c intro -->
  <div class="u-container">
    <div class="pd-intro" data-reveal>
      {intro}
    </div>
  </div>

  <!-- M-07d image sequence -->
{chr(10).join(blocks)}

  <!-- M-07e credits -->
  <div class="u-container">
    <dl class="credits">
{credits}
    </dl>

    <!-- M-07f prev / index / next -->
    <nav class="pd-nav" aria-label="Project navigation">
      <a href="project-{prev['slug']}.html">&lt; {esc(prev['title'])}</a>
      <a class="pd-nav__index" href="projects.html">All Projects</a>
      <a class="pd-nav__next" href="project-{nxt['slug']}.html">{esc(nxt['title'])} &gt;</a>
    </nav>
  </div>
"""


def page_about(S, A):
    def paras(lst):
        return "\n        ".join(f"<p>{esc(t)}</p>" for t in lst)

    principals = "\n".join(f"""      <article class="principal" data-reveal>
        {img('content/about/'+pr['photo'],'principal',pr['name'],cls='principal__img')}
        <div>
          <h3 class="principal__name">{esc(pr['name'])}</h3>
          <p class="principal__role">{esc(pr['role'])}</p>
          {paras(pr['paragraphs'])}
        </div>
      </article>""" for pr in A["principals"])

    team = "\n".join(f"""        <div class="team-card" data-reveal data-reveal-delay="{i%3}">
          {img('content/about/'+t['photo'],'team','',cls='team-card__img')}
          <p class="team-card__name">{esc(t['name'])}</p>
          <p class="team-card__role">{esc(t['role'])}</p>
        </div>""" for i, t in enumerate(A["team"]))

    return f"""
  <div class="u-container u-container--wide" {TOP_PAD}>

    <section class="about-section" id="firm">
      <header class="about-section__head"><h2 class="about-section__title">{esc(A['firm']['title'])}</h2></header>
      <div class="u-prose" data-reveal>
        {paras(A['firm']['paragraphs'])}
      </div>
    </section>

    <section class="about-section" id="philosophy">
      <header class="about-section__head"><h2 class="about-section__title">{esc(A['philosophy']['title'])}</h2></header>
      <div class="u-prose" data-reveal>
        {paras(A['philosophy']['paragraphs'])}
      </div>
    </section>

    <section class="about-section" id="principals">
      <header class="about-section__head"><h2 class="about-section__title">Principals</h2></header>
{principals}
    </section>

    <section class="about-section" id="team">
      <header class="about-section__head"><h2 class="about-section__title">Team</h2></header>
      <div class="grid grid--4">
{team}
      </div>
    </section>

  </div>
"""


def page_news(N):
    cards = "\n".join(news_card(n, i) for i, n in enumerate(N["highlights"]))
    return f"""
  <section class="u-container u-section" {TOP_PAD}>
    <div class="grid">
{cards}
    </div>
  </section>
"""


def page_reflist(heading, groups):
    out = []
    for g in groups:
        out.append(f'      <h2 class="reflist__year">{esc(g["group"])}</h2>')
        out += [f'      <p class="reflist__item">{it}</p>' for it in g["items"]]
    return f"""
  <section class="u-container u-section" {TOP_PAD}>
    <header class="about-section__head" data-reveal><h1 class="about-section__title">{esc(heading)}</h1></header>
    <div class="reflist" data-reveal data-reveal-delay="1">
{chr(10).join(out)}
    </div>
  </section>
"""


def page_contact(S):
    addr = "<br>".join(esc(a) for a in S["address"])
    return f"""
  <section class="u-container u-container--wide u-section" {TOP_PAD}>
    <div class="contact">

      <div class="contact__block" data-reveal>
        <h2 class="u-label">Studio</h2>
        <p>{addr}</p>
      </div>

      <div class="contact__block" data-reveal data-reveal-delay="1">
        <h2 class="u-label">Telephone</h2>
        <p><a class="contact__link" href="tel:{S['phone'].replace(' ','')}">{esc(S['phone'])}</a><br>
           <a class="contact__link" href="tel:{S['phoneAlt'].replace(' ','')}">{esc(S['phoneAlt'])}</a></p>
      </div>

      <div class="contact__block" data-reveal data-reveal-delay="2">
        <h2 class="u-label">New Project Enquiries</h2>
        <p><a class="contact__link" href="mailto:{S['enquiryEmail']}">{esc(S['enquiryEmail'])}</a><br>
           <a class="contact__link" href="mailto:{S['email']}">{esc(S['email'])}</a></p>
      </div>

      <div class="contact__block" data-reveal>
        <h2 class="u-label">Careers</h2>
        <p><a class="contact__link" href="mailto:{S['careersEmail']}">{esc(S['careersEmail'])}</a></p>
        <p style="margin-top:1em;color:var(--c-ink-mute)">{esc(S['careersNote'])}</p>
      </div>

      <div class="contact__map" role="img" aria-label="Map placeholder — replace with an embedded map"></div>
    </div>
  </section>
"""


# ------------------------------------------------------------------ sitemap --

def write_sitemap(S, pages):
    urls = "\n".join(f"  <url><loc>{S['domain']}/{p}</loc></url>" for p in pages if p != "404.html")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f'{urls}\n</urlset>\n')
    open(os.path.join(WEB, "sitemap.xml"), "w", encoding="utf-8").write(xml)


# -------------------------------------------------------------------- build --

def write(name, html, written):
    open(os.path.join(WEB, name), "w", encoding="utf-8").write(html)
    written.append(name)
    print(f"  {name:38} {len(html)//1024:>3} kb")


def build():
    S = load("site.json")
    A = load("about.json")
    N = load("news.json")
    P = load_projects()

    if not P:
        sys.exit("ERROR: no projects found in website/content/projects/")

    print(f"\nBuilding {WEB}")
    print(f"  {len(P)} projects, {len(N['highlights'])} news items\n")

    w = []
    B = S["brand"]

    write("index.html",
          head(S, f"{B} — {S['tagline']}", S["home"]["practiceText"][:150],
               preload="content/home/hero/01.jpg")
          + header(S, "home") + page_home(S, P, N) + footer(S), w)

    write("projects.html",
          head(S, f"Projects | {B}", "Selected architecture and interior projects.")
          + header(S, "projects", subnav_projects(S), sr_h1("Projects"))
          + page_projects(S, P) + footer(S), w)

    for i, p in enumerate(P):
        prev = P[i - 1]
        nxt  = P[(i + 1) % len(P)]
        write(f"project-{p['slug']}.html",
              head(S, f"{p['title']} | {B}",
                   (p.get("intro") or [""])[0][:150],
                   og_image=f"content/projects/{p['folder']}/{p.get('hero','hero.jpg')}",
                   preload=f"content/projects/{p['folder']}/{p.get('hero','hero.jpg')}")
              + header(S, "projects") + page_project(S, p, prev, nxt) + footer(S), w)

    write("about.html",
          head(S, f"About | {B}", "The firm, our design philosophy, principals and team.")
          + header(S, "about", subnav_about(), sr_h1("About " + B))
          + page_about(S, A) + footer(S), w)

    write("news.html",
          head(S, f"News | {B}", "Recent news, awards and press.")
          + header(S, "news", subnav_news("news.html"), sr_h1("News"))
          + page_news(N) + footer(S), w)

    for f_, key, title in [("press.html", "press", "Press"),
                           ("awards.html", "awards", "Awards"),
                           ("books.html", "books", "Books")]:
        write(f_, head(S, f"{title} | {B}", f"{title} and recognition.")
              + header(S, "news", subnav_news(f_))
              + page_reflist(title, N[key]) + footer(S), w)

    write("contact.html",
          head(S, f"Contact | {B}", "Studio address, telephone and enquiries.")
          + header(S, "contact", "", sr_h1("Contact"))
          + page_contact(S) + footer(S), w)

    write("404.html",
          head(S, f"Page not found | {B}", "Page not found.") + header(S, "")
          + f"""
  <section class="u-container u-section u-text-center" {TOP_PAD}>
    <h1 style="font-size:var(--fs-h1)">404</h1>
    <p style="margin-top:var(--sp-4)">This page does not exist.</p>
    <div class="pager"><a class="pager__btn" href="index.html">Back to Home</a></div>
  </section>
""" + footer(S), w)

    write_sitemap(S, w)
    open(os.path.join(WEB, "robots.txt"), "w").write(
        f"User-agent: *\nAllow: /\nSitemap: {S['domain']}/sitemap.xml\n")

    # Any project-*.html with no matching folder is an orphan — left behind by a
    # renamed or deleted project. We turn it into a redirect rather than deleting
    # it, so that anything already linking to the old URL (a bookmark, a search
    # result, an email) still lands somewhere useful instead of on a 404.
    valid = {f"project-{p['slug']}.html" for p in P}
    for f_ in glob.glob(os.path.join(WEB, "project-*.html")) + [os.path.join(WEB, "project-detail.html")]:
        name = os.path.basename(f_)
        if name in valid or not os.path.exists(f_):
            continue
        stub = (f'<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                f'<meta http-equiv="refresh" content="0; url=projects.html">\n'
                f'<link rel="canonical" href="{S["domain"]}/projects.html">\n'
                f'<title>Redirecting… | {esc(B)}</title>\n</head>\n<body>\n'
                f'<p>This project has moved. <a href="projects.html">View all projects</a>.</p>\n'
                f'</body>\n</html>\n')
        try:
            open(f_, "w", encoding="utf-8").write(stub)
            print(f"  {name:38}  -> redirect to projects.html (orphan)")
        except PermissionError:
            print(f"  ! could not rewrite orphan {name} — delete it by hand")

    print(f"\nDone. {len(w)} pages + sitemap.xml + robots.txt")
    print("Upload the whole 'website' folder to public_html.\n")


if __name__ == "__main__":
    build()

# Sample Portfolio — Website

A complete static website for the practice, plus the tooling to run it.
Plain HTML, CSS and JavaScript. No framework, no build toolchain, no monthly fee.

---

## The three things to know

**1. You edit content, not code.**
Everything you can change lives in `website/content/` — JSON files for words,
folders for pictures. The `.html` files are generated and get overwritten.

**2. One command turns content into the website.**
```bash
python3 tools/build.py
```

**3. One folder is the website.**
Upload the contents of `website/` to Hostinger's `public_html/`. That's the
whole deployment. Nothing else goes up.

---

## Folder map

```
sample-portfolio-website/
│
├── CLAUDE.md            instructions for Claude — read this before any AI session
├── README.md            you are here
│
├── docs/                every specification document
│   ├── 01-TEARDOWN.md        what the reference site is and what we copied
│   ├── 02-DESIGN-SYSTEM.md   colour, type, spacing, ratios, motion
│   ├── 03-MODULE-LIBRARY.md  the 15 UI components
│   ├── 04-PAGE-SPECS.md      the page templates
│   ├── 05-RESPONSIVE-SPEC.md breakpoints and mobile behaviour
│   ├── 06-CONTENT-GUIDE.md   ← START HERE to replace text and images
│   ├── 07-IMAGE-PIPELINE.md  ← how to bulk-process your photographs
│   ├── 08-DEPLOY.md          Hostinger upload, fonts, favicons, next steps
│   ├── 09-QC-CHECKLIST.md    what's verified, what needs your eyes
│   ├── 09-QC-CHECKLIST.md    what's verified, what needs your eyes
│   └── WHAT-I-NEED-FROM-YOU.md   ← the full list of content and images needed
│
├── intake/              ← fill-in forms for your content
│   ├── README.md            start here
│   ├── 01-studio-details.md
│   ├── 02-about.md
│   ├── 03-projects.md
│   └── 04-news-press-awards.md
│
├── website/             ★ THIS IS WHAT YOU UPLOAD
│   ├── *.html               generated — never edit by hand
│   ├── .htaccess            HTTPS, clean URLs, caching, security headers
│   ├── assets/css|js|fonts
│   └── content/         ★ THIS IS WHAT YOU EDIT
│       ├── site.json        brand, contact, categories, homepage
│       ├── about.json       the About page
│       ├── news.json        news, press, awards, books
│       ├── home/hero/       homepage slideshow
│       ├── about/           principal and team photos
│       ├── news/            news card images
│       └── projects/
│           └── 01-slug/     ONE FOLDER PER PROJECT
│               ├── project.json
│               ├── cover.jpg
│               ├── hero.jpg
│               └── gallery/
│
├── image-prep/          local tooling — NOT uploaded
│   ├── inbox/               drop full-size originals here
│   ├── archive/             originals kept safe after processing
│   ├── process.py           the bulk resizer
│   ├── studio.py            visual control panel
│   └── presets.json         sizes, ratios, file-size budgets
│
└── tools/
    ├── build.py             generates every .html
    └── validate.py          checks nothing is broken
```

`website/` is 5 MB with placeholder imagery. The whole project is 5.3 MB.

---

## Everyday commands

```bash
# See the site locally (needed — the category filter reads the URL)
cd website && python3 -m http.server 8000
#   → http://localhost:8000

# Bulk-resize new photographs
python3 image-prep/studio.py            # visual panel, opens in your browser
python3 image-prep/process.py           # or straight from the terminal
python3 image-prep/process.py --dry-run # show the plan, change nothing

# Rebuild the site after any content change
python3 tools/build.py

# Check nothing is broken
python3 tools/validate.py
```

One-time setup: `pip3 install --upgrade Pillow`

---

## Adding a project

```bash
# 1. Drop your photographs in
#      image-prep/inbox/projects/13-riverside-house/cover.jpg
#      image-prep/inbox/projects/13-riverside-house/hero.jpg
#      image-prep/inbox/projects/13-riverside-house/gallery/*.jpg

# 2. Resize everything
python3 image-prep/process.py

# 3. Copy a project.json from another project into
#    website/content/projects/13-riverside-house/ and edit it

# 4. Rebuild
python3 tools/build.py
```

The project page, the grid, the category filter, the prev/next links and the
sitemap all update on their own. There is no list to maintain — **the folders
are the list.**

Verified end to end: 9.6 MB of 6016×4016 300-DPI camera files went in, six
correctly-cropped 72-DPI web images under 210 KB each came out, and the new page
wired itself into the site with no HTML touched.

---

## What the image processor does

Point it at photographs of any size and it will, for each one:

- apply the EXIF rotation, then strip all metadata (including GPS)
- convert CMYK / 16-bit / transparent PNG to plain RGB
- crop to the exact ratio the slot needs — finding the most detailed region
  rather than blindly taking the centre
- resize to exact pixel dimensions and re-sharpen
- set 72 DPI
- search for the highest JPEG quality that still fits the size budget
- rename it, file it in the right place, and update the gallery list
- move your original to `archive/`, never deleting it

A 67 MB CMYK TIFF became a 226 KB progressive JPEG at 2400×1350 in the test run.

---

## What the site does

Fullscreen hero slider (autoplay, dots, keyboard, swipe, pauses off-screen),
two-tier navigation with keyboard-accessible dropdowns, contextual sub-nav that
becomes a scrollable strip on mobile, full-screen mobile menu with focus trap,
client-side project filtering with URL state, full-screen lightbox, scroll-spy
anchors, auto-hiding header, scroll reveals, lazy image fades.

All of it in one 16 KB vanilla JavaScript file. **This is finished and working —
it should be left alone.**

---

## Current status

**Passing:** all 21 pages validate — tag nesting, one `h1` each, no skipped
heading levels, `alt` on every image, `width`/`height` on every image (layout
shift = 0), no dead links, no missing images, presets matching the builder, no
undefined CSS variables, JavaScript syntax clean.

**Still to do, in priority order:**

0. **Fill in the `intake/` forms** — that's the full list of everything the site
   needs from you. See `docs/WHAT-I-NEED-FROM-YOU.md` for the reasoning
1. Replace the lorem ipsum — start with About → The Firm
2. Replace the placeholder photographs
3. Add the fonts (`website/assets/fonts/` — see `08-DEPLOY.md`)
4. Set your real domain in `site.json`
5. Add a favicon set
6. Check the five reconstructed design values in `09-QC-CHECKLIST.md` Part B


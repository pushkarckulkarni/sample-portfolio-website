# CLAUDE.md — Instructions for Claude working on this project

Read this first, every session. It is the contract for how this repository works.

---

## What this is

A static marketing website for **Sample Portfolio**, an architecture and interior
design practice. Plain HTML, CSS and vanilla JavaScript. No framework, no npm, no
build toolchain. It is hosted on **Hostinger shared hosting** by uploading the
`website/` folder to `public_html/`.

The design is modelled on the structure and interaction patterns of a reference
site. See `docs/01-TEARDOWN.md` for exactly what was and was not copied, and why.

---

## The one rule that matters

**`website/*.html` files are generated output. Never edit them by hand.**

They are produced by `tools/build.py` from JSON and image folders under
`website/content/`. Any manual edit is destroyed on the next build.

```
Edit content/*.json  ──►  python3 tools/build.py  ──►  website/*.html
```

If a user asks you to change page text, find the JSON field that produces it.
If a user asks you to change page *structure*, edit the relevant `page_*()`
function in `tools/build.py`.

---

## Repository layout

```
sample-portfolio-website/
├── CLAUDE.md              ← you are here
├── README.md              human quick-start
│
├── docs/                  ALL specification documents live here
│   ├── 01-TEARDOWN.md         what the reference site is, module by module
│   ├── 02-DESIGN-SYSTEM.md    tokens: colour, type, spacing, ratios, motion
│   ├── 03-MODULE-LIBRARY.md   the 15 UI components
│   ├── 04-PAGE-SPECS.md       the page templates
│   ├── 05-RESPONSIVE-SPEC.md  breakpoints and mobile behaviour
│   ├── 06-CONTENT-GUIDE.md    how the owner replaces text and images
│   ├── 07-IMAGE-PIPELINE.md   how the bulk image processor works
│   ├── 08-DEPLOY.md           Hostinger upload and post-launch checks
│   ├── 09-QC-CHECKLIST.md     what is verified, what needs human eyes
│   └── WHAT-I-NEED-FROM-YOU.md  the full content/image manifest
│
├── intake/                fill-in forms the owner completes; convert these
│                          into content/*.json when they're handed back
│
├── website/               ← THIS ENTIRE FOLDER IS WHAT GETS UPLOADED
│   ├── *.html                 GENERATED — do not edit
│   ├── sitemap.xml            GENERATED
│   ├── robots.txt             GENERATED
│   ├── .htaccess              hand-maintained (HTTPS, clean URLs, caching)
│   ├── assets/
│   │   ├── css/               tokens · base · components · responsive
│   │   ├── js/site.js         all behaviour, one file
│   │   └── fonts/             self-hosted woff2 (currently empty)
│   └── content/           ← THE SOURCE OF TRUTH
│       ├── site.json          brand, contact, categories, home page
│       ├── about.json         the About page
│       ├── news.json          news, press, awards, books
│       ├── home/hero/         homepage slides       (01.jpg, 02.jpg …)
│       ├── home/hero-mobile/  portrait crops for phones
│       ├── about/principals/  portraits
│       ├── about/team/        headshots
│       ├── news/              news card images
│       └── projects/
│           └── <NN-slug>/     ONE FOLDER PER PROJECT
│               ├── project.json    its title, text, credits, gallery order
│               ├── cover.jpg       grid thumbnail
│               ├── hero.jpg        page banner
│               └── gallery/*.jpg   the photo sequence
│
├── tools/
│   ├── build.py           generates every .html file
│   └── validate.py        static QC — run after every change
│
└── image-prep/            ← NOT uploaded. Local tooling only.
    ├── inbox/                 drop full-size originals here (mirrors content/)
    ├── archive/               originals moved here after processing
    ├── logs/                  CSV of every run
    ├── presets.json           pixel sizes, ratios, KB budgets per slot
    ├── process.py             the bulk processor
    ├── studio.py              local web control panel
    └── ui/index.html          the panel's front end
```

---

## Standard workflows

### Change wording on a page
1. Find the string in `website/content/*.json`.
2. Edit it.
3. `python3 tools/build.py`

### Add a project
1. Copy any folder in `website/content/projects/` → rename `NN-slug`.
2. Replace `cover.jpg`, `hero.jpg`, `gallery/*.jpg`.
3. Edit its `project.json`.
4. `python3 tools/build.py`

The grid, prev/next links, sitemap and category filter all update automatically.
There is no list of projects to maintain anywhere — the folders *are* the list.

### Process new photographs
1. Put originals in the matching `image-prep/inbox/` folder.
2. `python3 image-prep/process.py` (or `studio.py` for the GUI).
3. `python3 tools/build.py`

### Change the design
- Colour, type, spacing, ratios, motion → `website/assets/css/tokens.css` **only**.
- Component appearance → `website/assets/css/components.css`.
- Breakpoint behaviour → `website/assets/css/responsive.css`.
- **Never** hard-code a colour, size or duration outside `tokens.css`.

### Always finish with
```bash
python3 tools/validate.py
```

---

## Hard constraints

These are not preferences. Breaking any of them is a bug.

| Constraint | Why |
|---|---|
| No build step, no npm, no framework | Hostinger shared hosting; the owner is not a developer |
| Every `<img>` needs `width` + `height` | Keeps Cumulative Layout Shift at 0 |
| `DIMS` in `build.py` must match `presets.json` | Otherwise the declared size lies and the page jumps |
| No `maximum-scale` in the viewport meta | Blocks pinch-zoom; WCAG 1.4.4 failure |
| Exactly one `<h1>` per page, no skipped heading levels | Screen reader navigation |
| All colours/sizes/durations come from `tokens.css` | One place to change the design |
| `prefers-reduced-motion` must disable all motion | Handled once in `tokens.css` — don't duplicate per component |
| Content must be readable with JavaScript disabled | Progressive enhancement |
| Scroll listeners must be `{ passive: true }` | Non-passive listeners cause jank on mobile Safari |

---

## The JavaScript is finished — leave it alone

`website/assets/js/site.js` contains ten self-contained behaviours: header
auto-hide, mobile menu with focus trap, hero slider, project filter, lightbox,
scroll reveal, scroll-spy, back-to-top, lazy fade, load-more.

The owner has explicitly confirmed these all work correctly and asked that they
not be changed. Do not refactor, "improve", or restyle them without being asked
directly. If you must add a behaviour, add a new self-contained IIFE in the same
guarded style — if its markup isn't present, it no-ops.

---

## Known gaps — do not present these as done

1. **Fonts are not self-hosted yet.** `assets/fonts/` is empty; the CSS falls
   back to Futura / system-ui. Real Jost + Inter `.woff2` files are needed.
2. **All copy is lorem ipsum.** Every string in every JSON file is placeholder.
3. **All imagery is generated placeholder.** Grey abstract blocks.
4. **Five design values are reconstructions, not measurements** — header height,
   nav font-size/tracking, grid gutter, ink colour, typeface identity. The
   Chrome extension was not connected when the site was built. See
   `docs/09-QC-CHECKLIST.md` Part B.
5. **No favicon set.**
6. **Contact map is a grey placeholder div.**

The full manifest of what is still needed from the owner — every image slot and
every text field, with launch-minimum quantities — is in
`docs/WHAT-I-NEED-FROM-YOU.md`. The fill-in forms are in `intake/`. When the
owner hands one back, convert it into the matching `website/content/*.json` and
run the build; do not ask them to write JSON themselves.

---

## Tone when working with this user

They are building their firm's website and are not a developer. When you change
something:

- Say which **file** changed and what **command** to run.
- Don't explain the code unless asked.
- If a request would break one of the hard constraints above, say so plainly and
  offer the alternative rather than silently doing something different.
- If information is missing (a real project name, a real address), put a clearly
  marked placeholder in the JSON and tell them exactly which field to fill.

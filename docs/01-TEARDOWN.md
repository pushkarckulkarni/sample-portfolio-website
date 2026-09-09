# 01 — Reference Teardown

What the reference site actually is, module by module, so you can judge whether
the clone is faithful. Everything below was derived from a full crawl of the
live site's rendered HTML on 4 Aug 2026.

---

## 1. Technical profile of the original

| Item | Finding | Consequence for us |
|---|---|---|
| Platform | WordPress, custom theme a custom by Vibrant Info, design credited to *tsk design* | We are rebuilding static — none of the WP layer matters |
| Homepage slider | Slider Revolution 6.6.12 | Heavy commercial plugin. We replace it with a ~60-line vanilla crossfade — same behaviour, 400× lighter |
| Image delivery | KeyCDN (a third-party CDN) | We serve from Hostinger directly; use their CDN if traffic warrants |
| Lazy loading | Base64 1×1 GIF placeholders swapped by JS | Obsolete technique. We use native `loading="lazy"` — no JS, no layout shift |
| Viewport meta | `maximum-scale=1` | **Do not copy this.** It blocks pinch-zoom and is a WCAG 1.4.4 failure. Our build omits it |
| Content types | `project` (custom post type) + `project-category` taxonomy; `news`, plus flat pages for magazines / awards / books | Directly informs our content model — see doc 05 |

### Things the original does that we deliberately did **not** copy

1. **`maximum-scale=1`** — accessibility failure, blocks zoom.
2. **Base64 placeholder images** — makes every image invisible if JS fails.
3. **Empty `alt` on every image including the logo** — screen-reader hostile.
4. **`href="#"` on real navigation targets** (their News dropdown links to `//news` with a double slash) — broken.
5. **Slider Revolution** — ~300 KB of JS for a five-image fade.

These are bugs, not design decisions. Matching them would make the clone worse,
not more faithful.

---

## 2. Sitemap of the original

```
/                                   Home — fullscreen slider + news strip
/project/                           Projects index (paginated, /project/page/2/)
/project-category/{slug}/           Filtered index — houses, institutions,
                                    leisure, office, retail
/project/{slug}/                    Project detail
                                    (?cat=true appended when arriving from a
                                     category, so prev/next stays in-category)
/about/                             Single page, four anchor sections
/news/                              Highlights — card grid, paginated
/magazines/                         Long reference list, grouped Intl / Indian
/awards/                            Long reference list, grouped by year desc
/books/                             Long reference list, flat
/contact/                           Address, phones, email groups
```

**Our mapping** (categories renamed for an invention/design practice):

| Original | Ours |
|---|---|
| houses | residential |
| institutions | institutional |
| leisure | hospitality |
| office | workplace |
| retail | retail |
| /magazines/ | /press/ |

---

## 3. Navigation model — the important part

The reference uses a **two-tier, two-surface** navigation. Getting this right is
most of what makes the clone read as the same site.

### Tier 1 — primary nav (always visible)
`PROJECTS · ABOUT · NEWS · CONTACT`
Uppercase, small, heavily letter-spaced, right-aligned, logo left.

### Tier 2 — contextual sub-nav
Two of the four primary items have children, and those children are surfaced
**twice, simultaneously**:

- **As a hover dropdown** under the primary item (visible on any page).
- **As a horizontal tab row directly under the header**, but *only when you are
  inside that section*.

So on `/project/`, `PROJECTS` shows a dropdown on hover **and** a persistent
`All · Houses · Institutions · Leisure · Office · Retail` row is pinned under the
header. Same pattern on `/news/` with `Highlights · Magazines · Awards · Books`.

**About behaves differently**: its sub-nav row is `#firm · #design · #principals
· #team` — same visual treatment, but they are in-page anchors, not separate
pages. We added scroll-spy so the active tab tracks the section in view; the
original does not do this, and it is a straight improvement at zero cost.

**Contact has no sub-nav** — the header is one row tall on that page.

This means the header has **two possible heights** (84px and 124px on desktop).
Our tokens expose both as `--header-h` and `--header-h-sub`, and page top-padding
always references `--header-h-sub` so no page ever hides its first heading behind
the header regardless of which variant it uses.

---

## 4. Page-by-page structure

### Home
1. Fullscreen (100vh) image slider — 5–6 slides, crossfade, autoplay.
2. Below the fold: a news strip of three items linking to `/news`.
3. That is genuinely all. No "about" teaser, no services grid, no testimonials.

**Our version adds** a Selected Work grid and a one-paragraph practice statement
between the two. If you want strict parity, delete those two `<section>` blocks
from `index.html` — nothing else depends on them.

### Projects index
- Uniform grid of tiles. **3 across on desktop.**
- Each tile: image, then *below the image*, a title (`<h4>`) and a
  `Location, Year` caption in small uppercase grey.
- 12 items per page, then a "next page" arrow.
- Captions are **never overlaid** on the image. This is the single most
  characteristic choice of the layout — resist the urge to put text on the photo.

### Project detail — the richest template
Order is fixed:
1. Full-bleed hero image (no header offset; header floats over it).
2. Scroll-down cue.
3. Intro copy — centred, narrow measure, 4–14 paragraphs.
4. **Image sequence** — runs of full-bleed images, occasionally interrupted by a
   short pull-quote lifted from the body copy.
5. Credits: `Client`, `Project Details` (`Location, Year`).
6. Prev / All Projects / Next footer nav, using the real neighbouring project
   titles: `< Rama Greens Villa 08` … `Gulmohar Clubhouse >`.

### About
Four anchored sections, all prose except the last two:
`The Firm` (5 paras) · `Design Philosophy` (1 long para) ·
`Principals` (portrait + long bio, ×2) · `Team` (photo grid, name + role).

### News (Highlights)
Card grid. Each card is an image plus a **rich-text sentence with bold runs** —
not a headline + excerpt. e.g. *"**1Q1 Kitchen and Bar** wins the **Best Bar
Interior** in Bengaluru at the **NRAI India Nightlife Awards 2018**."*
Some cards link to an external PDF or article; some link nowhere.

### Awards / Magazines / Books
Single-column reference lists, no images.
- **Awards**: grouped by year, descending, year as a bold heading.
- **Magazines**: grouped `International:` / `Indian:`, publication name bold,
  then article title, author, page range, date.
- **Books**: flat list, title bold, then publisher, city, year.

These pages are long (Magazines runs to ~100 entries). Treat them as typography
exercises, not layout exercises.

### Contact
Address block, two phone numbers, then labelled email groups
(`New Project Enquiries`, `Career Opportunities`), plus a note about portfolio
file size. No form. No map.

**Our version adds a map placeholder.** Delete `.contact__map` for strict parity.

---

## 5. Footer

Minimal and identical everywhere: email address, copyright line, "Site by …"
credit, and a scroll-to-top control. Nothing else — no sitemap, no newsletter,
no social row. (Ours adds a small social row; remove it if unwanted.)

---

## 6. Values that could not be measured remotely

The Chrome extension was not connected during this build, so the following were
**not** read from live computed styles. They are informed reconstructions, and
each one is a 30-second check once you have the site open next to the reference.
The full checklist is in `07-QC-CHECKLIST.md`.

- Exact typeface (the original loads a licensed grotesque; we ship Jost + Inter)
- Exact nav font-size and letter-spacing
- Exact header height
- Exact grid gutter width
- Exact ink colour (we use `#1a1a1a`; theirs may be pure `#000`)

Everything structural — page count, nav model, grid columns, caption placement,
section order, breakpoint behaviour — came from the crawl and is accurate.

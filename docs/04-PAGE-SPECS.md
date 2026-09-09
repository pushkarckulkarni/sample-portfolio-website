# 04 — Page Specifications

Nine templates. For each: the file, the modules it uses in order, and the rules
that are easy to get wrong.

---

## P-01 · Home → `index.html`

| # | Module | Notes |
|---|---|---|
| 1 | M-04 Hero Slider | 5 slides, 6s interval, full viewport |
| 2 | M-05 Grid | "Selected Work", 6 tiles, `--dim` on |
| 3 | Practice statement | One paragraph at `--max-prose`, centred |
| 4 | M-10 News cards | 3 latest |
| 5 | M-12 Footer | |

- The hero starts at `y = 0`. The header floats over it with **no** background
  until scroll — hence the transparent-until-`.is-scrolled` treatment.
- Hero images are the LCP. Slide 1 gets `fetchpriority="high"` and a `<link
  rel="preload">`; slides 2–5 are `loading="lazy"`.
- Sections 2 and 3 are **additions to the reference**, which has only a slider
  and a news strip. Delete those two `<section>` blocks for strict parity.

---

## P-02 · Projects Index → `projects.html`

| # | Module |
|---|---|
| 1 | M-01 Header + M-02 Sub-nav (category tabs) |
| 2 | M-05 Grid, 12 tiles |
| 3 | M-06 Load More |
| 4 | M-12 Footer |

- Page content starts at `calc(var(--header-h-sub) + var(--sp-8))`.
- Each card carries `data-cats="residential"` (space-separated for multi-category).
- Filtering is **progressive enhancement**: tabs are real links to
  `projects.html?cat=x`. JS intercepts the click, filters in place, and rewrites
  the URL with `history.replaceState`. With JS off, the links still navigate.
- A visually-hidden `aria-live` region announces "8 projects" after each filter —
  otherwise a screen reader gets no feedback that anything happened.
- Sort order is reverse-chronological by year. Always.

---

## P-03 · Project Detail → `project-detail.html`

The template that carries the practice. Order is fixed (see M-07).

**Content rules**
- Intro copy: 3–14 paragraphs. This is where the architecture is explained;
  under-writing it makes the whole site feel thin.
- Image count: 8–20. Fewer than 8 and the sequence has no rhythm.
- Pull quote must be lifted verbatim from the intro copy — it is a repetition for
  emphasis, not new copy.
- Credits: Location, Year, Area, Client, Team, Photography.
- Prev/Next must show **real neighbouring project titles**, never "Previous" and
  "Next" alone.

**Technical**
- The hero has no top padding — it sits under the floating header by design.
- All body images are `[data-lightbox]` and get `cursor: zoom-in`.
- Preserve the `?cat=` query when arriving from a filtered index so prev/next
  stays inside the category (the reference does this with `?cat=true`).

---

## P-04 · About → `about.html`

Four anchored sections: `#firm`, `#philosophy`, `#principals`, `#team`.

- Sub-nav (M-02) holds in-page anchors with **scroll-spy** — the observer uses
  `rootMargin: -45% 0px -50% 0px` so the active tab flips when a section crosses
  the vertical middle of the viewport, not its top edge.
- `html { scroll-padding-top }` and `.about-section { scroll-margin-top }` both
  clear the fixed header. You need both: one for anchor clicks, one for
  `scrollIntoView` and browser restore.
- Principals: portrait + 2–3 paragraph bio each.
- Team: 8 cards, 4-up desktop, greyscale → colour on hover.

---

## P-05 · News → `news.html`

- Sub-nav tabs: Highlights / Press / Awards / Books.
- 3-column card grid, 9 items, then Load More.
- Card copy uses `<strong>` for project names, awards and publications — that
  bolding *is* the visual hierarchy.

---

## P-06/07/08 · Press · Awards · Books

All three use M-10 `.reflist` — single column at `--max-prose`, no images.

| Page | Grouping |
|---|---|
| Press | `International` / `Domestic` |
| Awards | By year, descending |
| Books | Flat, reverse-chronological |

Publication or award name in `<strong>`, remainder in regular weight.

---

## P-09 · Contact → `contact.html`

- No sub-nav — header is one row here.
- Four blocks: Studio address / Telephone / New Project Enquiries / Careers.
- No contact form. A firm at this level takes email; a form implies a queue.
- Map is a greyscaled placeholder — swap in an iframe or a static image.
  If you embed Google Maps, load it **on click**, not on page load, or you hand
  every visitor a third-party cookie before they've consented.

---

## P-10 · 404 → `404.html`

Centred, minimal, one button back to Home. Wired up in `.htaccess`.

---

## Global rules

**Every page**
- `<a class="skip-link">` is the first focusable element.
- Exactly one `<h1>`.
- Every `<img>` has explicit `width`/`height` — CLS must stay at 0.
- Decorative images get `alt=""`; content images get real alt text.
- Top padding on non-hero pages is `calc(var(--header-h-sub) + var(--sp-8))`,
  even when that page has no sub-nav. Using the taller value everywhere means no
  page can ever hide its first heading, and the 20px of extra air is invisible.

**Page weight budget**

| Page | Target |
|---|---|
| Home | < 1.2 MB |
| Projects index | < 900 KB |
| Project detail | < 2.5 MB |
| About | < 700 KB |
| Text pages | < 200 KB |

**Not built, and why**

- *Search* — under ~60 projects, category tabs beat search.
- *Blog / journal* — News covers it.
- *Multi-language* — add only if there's a real second audience.
- *CMS* — see `06-BUILD-HANDOFF.md` for when to add one.

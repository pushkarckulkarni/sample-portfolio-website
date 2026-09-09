# 03 — Module Library

Fifteen modules build every page. Each has an ID (`M-01`…`M-15`) that appears as
a comment in `components.css` and in the page HTML, so you can always trace a
rendered element back to its spec.

Naming is BEM-ish: `.block`, `.block__element`, `.block--modifier`, `.is-state`.

---

## M-01 · Site Header

**Markup** `header.site-header > .site-header__bar > .site-logo + .nav-primary + .nav-toggle`

Fixed to the top, full-bleed, white, `z-index: 200`.

| Property | Desktop | Mobile (<900px) |
|---|---|---|
| Height | 84px (`--header-h`) | 60px (`--header-h-mob`) |
| Logo | left, uppercase, `.2em` tracking | same, tagline hidden <600px |
| Nav | right, horizontal | replaced by burger |

**Behaviours**
- `.is-scrolled` — adds a 1px bottom hairline once `scrollY > 4`. Keeps the top
  of a full-bleed hero completely clean.
- `.is-hidden` — translates the header off-screen on scroll-down past 240px,
  restores on scroll-up. Gives the images the full viewport while browsing, and
  puts navigation one flick away. Suppressed while the mobile menu is open.
- Underline on nav links grows from the left (`transform: scaleX`), and is
  permanently on for `.is-active`.

**Dropdown (`.nav-drop`)** opens on `:hover` **and** `:focus-within`, so it is
keyboard-reachable. Hidden entirely on `hover: none` devices.

**Accessibility** — `nav[aria-label="Primary"]`; burger carries `aria-expanded`
and `aria-controls`; a skip link is the first focusable element on every page.

---

## M-02 · Sub-navigation / Filter Tabs

**Markup** `nav.subnav > ul.subnav__list > li.subnav__item > a.subnav__link`

Second row inside the fixed header shell, separated by a hairline. Centred on
desktop; on mobile it becomes a horizontally scrollable strip with hidden
scrollbars and `scroll-snap-type: x proximity`. A trailing `::after` spacer keeps
the last tab clear of the screen edge.

Three uses, identical appearance:
1. **Projects** — category filter. Real `href`s, enhanced by JS (M-filter).
2. **News** — page tabs. Plain links, no JS.
3. **About** — in-page anchors, with scroll-spy.

Active state is `colour: --c-ink` plus a 1px bottom border.

---

## M-03 · Mobile Menu

Full-screen overlay panel, `backdrop-filter: blur(8px)`, `z-index: 300`.

- Links stagger in at 45ms intervals via an inline `--i` custom property set by JS.
- Body gets `.is-locked` (`overflow: hidden`) while open.
- Sub-items appear as an indented group under their parent — no accordion, no
  second tap. On a phone, revealing everything at once is faster than nesting.
- Closes on: link click, Escape, burger tap, or viewport crossing 900px.
- **Focus is trapped** while open, and returns to the burger on close.

---

## M-04 · Hero Slider

**Markup** `section.hero[data-interval] > .hero__slide × N + .hero__scrim + .hero__nav × 2 + .hero__caption + .hero__dots + .hero__cue`

- Height `100svh` — `svh` not `vh`, so the iOS address bar doesn't cause a jump.
- Slides are absolutely stacked; **only `opacity` animates** (1200ms). This stays
  on the compositor and holds 60fps on low-end Android.
- Ken Burns: the active slide's `<img>` transitions `scale(1.06) → scale(1)` over
  7s. Subtle enough to read as breathing rather than as an effect.
- Caption bottom-left over a bottom-anchored gradient scrim; dots bottom-right;
  scroll cue bottom-centre with a drawing-line animation.
- Invisible 14%-wide click zones on the left and right edges (desktop only).

**Controls**: dots, edge clicks, arrow keys, touch swipe (45px threshold).
Autoplay pauses when the tab is hidden or the hero scrolls out of view
(IntersectionObserver), and restarts after any manual input.

**Mobile** switches to a 4:5 portrait crop — a 16:9 band on a tall phone screen
wastes the format. Scroll cue is hidden.

---

## M-05 · Project Grid & Card

**Markup** `.grid > a.card > .card__media > img.card__img` then `.card__body > h4.card__title + p.card__meta`

| Viewport | Columns |
|---|---|
| ≥ 900px | 3 |
| 700–899px | 2 |
| < 700px | 1 |

- Tile is a locked 4:3 box with `overflow: hidden`; the image is `object-fit: cover`.
- **Caption sits below the image, left-aligned, never overlaid.** This is the
  defining move of the layout.
- Hover: image scales to 1.03 over 700ms. On `.grid--dim`, all *other* cards drop
  to 55% opacity — the classic portfolio focus effect. Disabled on touch.

**States**: `.is-hidden` (filtered out), `[data-batch-hidden]` (not yet paged in).

---

## M-06 · Pagination / Load More

Centred, bordered, uppercase button. Fills solid black on hover. Carries a real
`disabled` attribute when there is nothing more to load — the control never lies
about there being more work.

---

## M-07 · Project Detail Blocks

The richest template. Seven sub-blocks, fixed order:

| Sub-block | Class | Notes |
|---|---|---|
| a. Hero | `.pd-hero` | 82svh, full-bleed, header floats over it, **no top padding** |
| b. Title | `.pd-head` | Centred desktop, left-aligned <700px |
| c. Intro | `.pd-intro` | Capped at `--max-prose`, `--fs-lead` |
| d. Sequence | `.figure`, `.figure-pair` | Alternate `--full` / `--wide` / pairs for rhythm |
| e. Quote | `.pullquote` | Capped at `--max-narrow`, centred |
| f. Credits | `.credits` | `auto-fit minmax(200px, 1fr)` — reflows to 1 col on phone |
| g. Prev/Next | `.pd-nav` | 3-col grid; stacks and centres below 520px |

**Rhythm rule:** never place more than two full-bleed images in a row without
interrupting with a pair or a quote. Monotony is the failure mode of this
template.

`.figure-pair` is a 2-col grid that collapses to 1 below 700px. All `--wide` and
`--narrow` figures go full-bleed below 900px.

---

## M-08 · Lightbox

Built entirely by JS — no markup in the page. Attaches to every `[data-lightbox]`
image.

- `role="dialog"` + `aria-modal="true"`, focus moves to the close button on open
  and returns to the trigger on close.
- Escape / arrow keys / click-outside / swipe.
- `1 / 12` counter bottom-centre.
- Triggers get `tabindex="0"` and `role="button"` plus Enter/Space handling.
- On phones the prev/next arrows move to the **bottom corners** — mid-height
  arrows sit exactly where a thumb drags to scroll.

---

## M-09 · About Blocks

- `.about-section` — hairline-separated, `scroll-margin-top` set to clear the
  fixed header so anchor jumps never bury the heading.
- `.principal` — `340px` portrait column + fluid bio column; stacks below 900px
  with the portrait capped at 320px.
- `.team-card` — 1:1 photo, 4-up desktop / 3-up ≤1200px / 2-up ≤700px.
  **Greyscale by default, colour on hover.** Removed entirely on touch devices,
  where there is no hover to reveal it.

---

## M-10 · News & Reference Lists

**`.news-card`** — 4:3 image, then a rich-text sentence with `<strong>` runs
(matching the reference's editorial voice), then a date in small caps. It is a
sentence, not a headline-plus-excerpt.

**`.reflist`** — for Awards / Press / Books. Single column at `--max-prose`,
grouped by `.reflist__year` headings (uppercase, tracked, hairline underline).
These pages get long (100+ entries); they are a typography problem, not a layout
problem.

---

## M-11 · Contact

`auto-fit minmax(240px, 1fr)` grid of labelled blocks — collapses 4 → 2 → 1
without a single media query. Links get a hairline underline that darkens on
hover. `.contact__map` spans the full row at 21:9 (4:3 on phone), greyscaled to
match the palette.

---

## M-12 · Site Footer

One flex row: email · social · copyright. `flex-wrap` handles tablet;
below 900px it stacks left-aligned. Deliberately minimal — no sitemap, no
newsletter capture.

---

## M-13 · Back to Top

44×44 fixed button, bottom-right. Appears past 60% of viewport height. 44px is
the minimum comfortable touch target.

---

## M-14 · Scroll Reveal

Opt-in via `[data-reveal]`; IntersectionObserver adds `.is-in`. Optional
`data-reveal-delay="1|2|3"` gives a 90ms stagger for grid rows.

**Fails safe**: if IntersectionObserver is missing *or* reduced-motion is set,
everything is marked visible immediately. Content is never hidden by a
broken script.

---

## M-15 · Lazy Image Fade

Native `loading="lazy"` plus a JS-applied `.is-loaded` class for a 320ms fade-in.
Images already in cache are detected via `img.complete` and skip the fade, so
back-navigation doesn't flicker.

---

## Adding a new module

1. Add the CSS block to `components.css` with a numbered banner comment.
2. Reference only tokens — no literal colours, sizes or durations.
3. Add responsive overrides to `responsive.css`, not inline in the module.
4. Document it here.
5. Add its interaction to the QC checklist in `07-QC-CHECKLIST.md`.

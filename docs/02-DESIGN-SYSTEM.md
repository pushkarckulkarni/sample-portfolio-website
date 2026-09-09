# 02 — Design System

Everything here is already implemented in `site/assets/css/tokens.css`.
This document explains *why* each value is what it is, so you can change them
without breaking the proportions.

---

## The governing idea

An architecture portfolio has exactly one job: get out of the way of the
photographs. Every decision below follows from that.

- **Monochrome.** No brand colour anywhere. The colour comes from the work.
- **One weight range.** Nothing below 300, nothing above 500. Bold type would
  compete with the images.
- **Type as texture, not as voice.** All chrome (nav, labels, captions) is small,
  uppercase and tracked out hard. It reads as a fine grey line, not as words.
- **Generous, asymmetric whitespace.** Vertical rhythm is ~2× what a marketing
  site would use. This is what makes a grid of photos feel curated.
- **Motion under 350ms, opacity only.** No spring, no bounce, no parallax.

---

## Colour

| Token | Value | Used for |
|---|---|---|
| `--c-bg` | `#ffffff` | Page and header background |
| `--c-bg-alt` | `#f4f3f1` | Image placeholder while loading — warm, not blue-grey |
| `--c-ink` | `#1a1a1a` | Headings, logo, active nav |
| `--c-ink-soft` | `#4a4a4a` | Body paragraphs |
| `--c-ink-mute` | `#8c8c8c` | Captions, meta, inactive nav |
| `--c-rule` | `#e2e0dc` | Hairline dividers |
| `--c-rule-strong` | `#c9c6c0` | Button borders |
| `--c-scrim` | `rgba(0,0,0,.86)` | Lightbox backdrop |

**Why `#1a1a1a` and not `#000`:** pure black on pure white at large sizes creates
halation on LCD panels and reads as harsh. `#1a1a1a` is indistinguishable in
isolation and noticeably calmer in a page full of photographs.

**Contrast check:** `--c-ink-mute` on white is 3.5:1 — this passes WCAG AA for
large text but **fails for body copy**. It is used *only* for captions and meta
at ≥12px uppercase, which is acceptable under 1.4.3's large-text provision when
tracked. Never use it for a paragraph.

---

## Typography

### The two families

| Role | Family | Why |
|---|---|---|
| `--font-ui` | **Jost** (300/400/500) | Geometric grotesque in the Futura lineage. Uppercase + wide tracking is exactly what this genre wants. Open-source, so no licensing exposure. |
| `--font-body` | **Inter** (300/400) | Neutral, high x-height, designed for screen. Disappears behind the content, which is the point. |

Fallback stacks are `Futura / Century Gothic / Avenir Next` and
`system-ui / Segoe UI / Helvetica`, so the page is still visually correct before
the webfonts land.

**Self-host both.** `assets/fonts/*.woff2`, referenced by `@font-face` in
`base.css`. On Hostinger shared hosting a Google Fonts round-trip costs
200–400ms on Indian mobile networks; a self-hosted woff2 costs nothing.

### Scale

Ratio **1.25 (major third)** off a 16px base. Every step is `clamp()`d between
the 480px and 1440px viewports, so type scales continuously and no size needs a
media-query override.

| Token | Range | Use |
|---|---|---|
| `--fs-nano` | 11px (12px mobile) | Nav, tabs, buttons, section labels |
| `--fs-micro` | 12px | Image captions, project meta, footer |
| `--fs-small` | 13px | Reference lists, credits |
| `--fs-body` | 14 → 16px | Paragraphs |
| `--fs-lead` | 16 → 20px | Project intro copy |
| `--fs-h4` | 15 → 17px | Card titles |
| `--fs-h3` | 18 → 24px | Principal names |
| `--fs-h2` | 22 → 34px | Hero caption, section headings |
| `--fs-h1` | 28 → 52px | Project detail title |
| `--fs-quote` | 18 → 28px | Pull quotes |

Note the nav goes *up* on mobile (11→12px). Small tracked uppercase becomes
illegible at arm's length on a phone; this is a deliberate inversion.

### Letter-spacing — the signature

| Token | Value | Applied to |
|---|---|---|
| `--ls-chrome` | `.16em` | Primary nav, section labels, buttons |
| `--ls-tab` | `.12em` | Sub-nav tabs, dropdowns |
| `--ls-caption` | `.08em` | Captions, meta, footer |
| `--ls-title` | `.02em` | Card titles |
| `--ls-body` | `0` | Paragraphs |

Rule of thumb: **the smaller and more uppercase the type, the more tracking it
needs.** Never track lowercase body copy.

### Line height

`1.75` for body copy. This is unusually loose and it is the correct call — long
paragraphs at 14–16px against lots of white need the air. `1.15` for display
headings, `1.2` for nav.

---

## Spacing

4px base scale: `4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96 · 128 · 160`.
Use only these. Arbitrary values are how a grid loses its rhythm.

Section padding is fluid:
- `--section-y` → `clamp(48px, 3vw + 32px, 112px)`
- `--section-y-lg` → `clamp(64px, 5vw + 40px, 160px)`

Gutter: `clamp(16px, 4vw, 56px)`. On a 375px phone that is 16px; on a 1440px
desktop, 56px.

---

## Layout & measure

| Token | Value | Use |
|---|---|---|
| `--max-page` | 1600px | Project and news grids |
| `--max-wide` | 1320px | About sections, credits |
| `--max-prose` | 68ch | Body copy — **the important one** |
| `--max-narrow` | 46ch | Pull quotes |

`68ch` lands around 62–68 characters per line, which is the readability sweet
spot. Using `ch` rather than `px` means the measure stays correct if you change
the body font size later.

---

## Aspect ratios

Locked, never inferred from the file. This is what makes a grid look designed
rather than assembled.

| Token | Ratio | Use |
|---|---|---|
| `--ar-hero` | 16:9 | Homepage slider, desktop |
| `--ar-hero-mob` | 4:5 | Homepage slider, phone (portrait crop) |
| `--ar-card` | 4:3 | Project grid tile |
| `--ar-detail` | 3:2 | Project detail image (4:3 on phone) |
| `--ar-portrait` | 4:5 | Principal photo |
| `--ar-square` | 1:1 | Team photo |
| `--ar-news` | 4:3 | News card |

Every `<img>` also carries explicit `width` and `height` attributes. Combined
with `aspect-ratio` in CSS this gives a **CLS of 0** — the layout never jumps as
images load. Do not omit them.

---

## Image production spec

| Slot | Export at | Display | Format |
|---|---|---|---|
| Hero | 2400×1350 | 100vw | AVIF + WebP + JPEG fallback |
| Hero (mobile) | 1200×1500 | 100vw | same |
| Grid tile | 1200×900 | ~33vw | same |
| Detail | 2000×1333 | 100vw | same |
| Principal | 900×1125 | ~340px | same |
| Team | 700×700 | ~25vw | same |

Target ≤ 220 KB for heroes, ≤ 90 KB for tiles, JPEG quality 78–82. Total
homepage payload should stay under 1.2 MB.

---

## Motion

| Token | Duration | Use |
|---|---|---|
| `--dur-fast` | 180ms | Colour and opacity on hover |
| `--dur-base` | 320ms | Menus, dropdowns, lightbox |
| `--dur-slow` | 700ms | Image zoom, scroll reveal |
| `--dur-hero` | 1200ms | Slider crossfade |

Easing is `cubic-bezier(.22,.61,.36,1)` — a plain ease-out. Hover zoom is capped
at `1.03`; anything more looks like a consumer site.

**`prefers-reduced-motion` collapses every duration to 1ms and sets the zoom to
1.** This is handled once in `tokens.css` and therefore applies everywhere
automatically. Do not write per-component reduced-motion rules.

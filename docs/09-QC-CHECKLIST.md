# 07 — QC Checklist

Two parts: what has already been verified automatically, and what still needs a
human with the reference site open in the next tab.

---

## Part A · Automated checks — all passing

Run against all 10 pages on 4 Aug 2026.

| Check | Result |
|---|---|
| HTML tag nesting (all pages) | 0 errors |
| Exactly one `<h1>` per page | 10/10 |
| No skipped heading levels | 10/10 |
| Every `<img>` has `alt` | 53/53 |
| Every `<img>` has `width` + `height` (CLS = 0) | 53/53 |
| Internal links resolve to a real file | 0 dead |
| Referenced assets exist | 0 missing |
| Every interactive control has an accessible name | pass |
| No `maximum-scale` (zoom not blocked) | pass |
| CSS braces balanced | 267/267 pairs |
| CSS custom properties: used-but-undefined | 0 |
| Hard-coded colours outside `tokens.css` | 0 (excl. print) |
| `site.js` syntax | pass (`node --check`) |

**Re-run after any change:**

```bash
cd site && python3 ../tools/validate.py   # if you keep the script
```

---

## Part B · Manual checks against the reference

The Chrome extension was not connected during this build, so the five values
below were reconstructed rather than measured. Open the reference site and
the prototype side by side at 1440px and check each. Each is a ~30-second fix.

| # | What to measure | Our value | How |
|---|---|---|---|
| B1 | Header height | `--header-h: 84px` | Inspect their `<header>`, read the computed height |
| B2 | Nav font-size + tracking | `11px` / `.16em` | Inspect a nav link, read `font-size` and `letter-spacing` |
| B3 | Grid gutter | `clamp(12px,1.6vw,28px)` | Measure the gap between two project tiles |
| B4 | Body ink colour | `#1a1a1a` / `#4a4a4a` | Eyedrop a paragraph |
| B5 | Typeface identity | Jost + Inter | Inspect `font-family`. If it's licensed, either buy it or keep Jost |

Adjust in `tokens.css` only. Every module reads from there, so the whole site
updates at once.

---

## Part C · Interaction test script

Walk this once per browser. Chrome, Safari, Firefox, plus real iOS Safari and
real Android Chrome — device emulators do not reproduce touch or the iOS
viewport correctly.

### Header
- [ ] Hairline appears once you scroll past ~4px
- [ ] Header slides away on scroll-down past 240px, returns on scroll-up
- [ ] Header does **not** hide while the mobile menu is open
- [ ] Active page's nav item shows a permanent underline
- [ ] Hovering a nav link grows the underline from the left

### Dropdowns (desktop)
- [ ] `PROJECTS` and `NEWS` open on hover
- [ ] They also open on **keyboard focus** (Tab to the link)
- [ ] They do not appear at all on a touch device

### Mobile menu (< 900px)
- [ ] Burger animates to an X
- [ ] Links stagger in
- [ ] Background scroll is locked while open
- [ ] Escape closes it and focus returns to the burger
- [ ] Tab cycles **inside** the menu and cannot escape behind it
- [ ] Resizing past 900px auto-closes it

### Hero slider
- [ ] Autoplays at 6s, crossfade only, no horizontal movement
- [ ] Ken Burns scale is subtle — if you notice it, it's too strong
- [ ] Dots change the slide and reflect the active one
- [ ] Left/right edge clicks work (desktop)
- [ ] Swipe works (touch)
- [ ] Arrow keys work when the hero has focus
- [ ] **Pauses when scrolled out of view**
- [ ] **Pauses when the browser tab is hidden**
- [ ] Restarts its timer after any manual input
- [ ] Switches to a 4:5 portrait crop below 700px

### Project filter
- [ ] Tabs filter the grid in place, no page reload
- [ ] URL updates to `?cat=residential`
- [ ] Reloading that URL restores the filter
- [ ] With JS disabled, the tabs still navigate as plain links
- [ ] A screen reader announces the new count

### Lightbox
- [ ] Clicking a detail image opens it
- [ ] Enter/Space on a focused image opens it
- [ ] Arrows, Escape, click-outside, swipe all work
- [ ] Counter reads `n / total` correctly
- [ ] Focus starts on Close and returns to the image on close
- [ ] Below 700px the arrows are in the bottom corners

### About
- [ ] Anchor tabs jump to the section with the heading **clear of the header**
- [ ] Scroll-spy highlights the section in view
- [ ] Team photos are greyscale, colourise on hover, stay colour on touch

### Global
- [ ] Back-to-top appears past 60% viewport height and scrolls smoothly
- [ ] Scroll reveals fire once and do not re-trigger
- [ ] With `prefers-reduced-motion: reduce`: **no** animation anywhere, and
      **all** content is still visible
- [ ] With JS entirely disabled: all content is readable, all links work

---

## Part D · Responsive sweep

Test at these exact widths. See `05-RESPONSIVE-SPEC.md` for what should change.

`1920 · 1440 · 1280 · 1024 · 900 · 899 · 834 · 768 · 700 · 699 · 430 · 390 · 375 · 320`

At every single one:
- [ ] No horizontal scrollbar
- [ ] No clipped or overlapping text
- [ ] No squashed or stretched image
- [ ] All touch targets ≥ 44×44px
- [ ] Header never covers the first heading

The 899/900 and 699/700 pairs are the ones that break. Check them adjacent.

---

## Part E · Performance

Run PageSpeed Insights (mobile) on the deployed URL.

| Metric | Target |
|---|---|
| LCP | < 2.5s |
| CLS | < 0.05 |
| INP | < 200ms |
| Performance score | > 90 |
| Total page weight (home) | < 1.2 MB |

If LCP is slow, it is almost certainly the hero image. Check that slide 1 is
preloaded, has `fetchpriority="high"`, is **not** `loading="lazy"`, and is served
as AVIF.

---

## Part F · Pre-launch

- [ ] Every lorem ipsum string replaced
- [ ] Real photography at the specified aspect ratios
- [ ] Fonts self-hosted in `assets/fonts/`
- [ ] Favicon set (`.ico`, 180px apple-touch, 512px PNG, `site.webmanifest`)
- [ ] `sitemap.xml` written and referenced in `robots.txt`
- [ ] Unique `<title>` and `meta description` per page
- [ ] `og:image` per page (1200×630)
- [ ] Canonical URLs point at the live domain, not `sampleportfolio.com` placeholder
- [ ] SSL installed, Force HTTPS on
- [ ] `http://`, `www.` both redirect to canonical
- [ ] Clean URLs working (`/about` not `/about.html`)
- [ ] 404 page serves
- [ ] Analytics installed (Plausible or Fathom — no cookie banner needed;
      GA4 requires one)
- [ ] Tested on a real iPhone and a real Android phone
- [ ] Someone who has never seen the site can find a project in under 15 seconds

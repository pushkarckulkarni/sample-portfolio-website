# 05 — Responsive Specification

The reference site is a desktop-first WordPress theme that degrades to mobile.
Ours is built the other way round: fluid by default, with breakpoints used only
where a *layout* has to change — not where a *size* has to change.

---

## Why there are so few breakpoints

Sizes are handled by `clamp()` in `tokens.css`. Type, gutters, and section
padding scale continuously between 480px and 1440px. That removes the usual
20-odd typography media queries and, more importantly, removes the awkward
in-between states where a layout is technically "desktop" but the type is still
phone-sized.

Breakpoints are reserved for the four things that genuinely cannot be fluid:

1. Column count
2. Navigation mode (horizontal ↔ burger)
3. Element order and stacking
4. Aspect-ratio changes

---

## Breakpoints

| Name | Query | What changes |
|---|---|---|
| **xl** | ≥ 1440px | Nothing — grid caps at `--max-page` (1600px) |
| **lg** | ≤ 1199px | Team grid 4 → 3; principal portrait 340 → 280px |
| **md** | ≤ 899px | **Nav → burger.** Project grid 3 → 2. Detail figures all full-bleed. Principal stacks. Footer stacks. |
| **sm** | ≤ 699px | Everything → 1 column. Figure pairs stack. Hero → 4:5 portrait. Detail images → 4:3. |
| **xs** | ≤ 519px | Team 2-up. Credits 1 col. Prev/next stacks and centres. |

**899px is the important one.** Below it the site is a different navigation
product. Test it hardest.

---

## Grid behaviour

| Grid | ≥900 | 700–899 | <700 | <520 |
|---|---|---|---|---|
| Project (`.grid`) | 3 | 2 | 1 | 1 |
| News (`.grid`) | 3 | 2 | 1 | 1 |
| Team (`.grid--4`) | 4 (3 ≤1199) | 2 | 2 | 2 |
| Figure pair | 2 | 2 | 1 | 1 |
| Credits | auto-fit | auto-fit | auto-fit | 1 |
| Contact | auto-fit | auto-fit | 1 | 1 |

Credits and Contact use `repeat(auto-fit, minmax(Npx, 1fr))` and therefore need
no breakpoints at all above `xs`. Prefer this pattern for any new grid where the
column count doesn't have to be exact.

---

## Navigation across viewports

### ≥ 900px
Horizontal nav, right-aligned. Dropdowns on hover *and* focus-within. Sub-nav row
centred beneath.

### < 900px
- `.nav-primary` → `display: none`; `.nav-toggle` → `display: block`.
- Header shrinks 84 → 60px.
- Sub-nav **stays visible** and becomes a horizontally scrollable strip:
  `justify-content: flex-start`, hidden scrollbar, `scroll-snap-type: x
  proximity`, trailing spacer so the final tab clears the edge.
- Tapping the burger opens the full-screen panel (M-03) with all primary and
  sub-items exposed at once — no accordion. One tap to anything.

**Why keep the sub-nav on mobile** rather than folding it into the burger: on a
category-filtered projects page the current filter is essential context. Hiding
it behind a menu means the user forgets what they're looking at.

---

## Hero across viewports

| Viewport | Height | Ratio | Cue | Edge zones |
|---|---|---|---|---|
| ≥ 900px | `100svh` | 16:9 crop | shown | shown |
| 700–899 | `72svh` | 16:9 crop | hidden | hidden |
| < 700px | auto | **4:5 portrait** | hidden | hidden (swipe only) |

Use `svh`, not `vh`. On iOS Safari `100vh` is the *largest* possible viewport, so
a `100vh` hero is taller than the visible screen and the scroll cue sits below
the fold on first paint. `svh` is the smallest viewport and is correct.

Below 700px the hero switches to a **portrait crop**. A 16:9 band on a 390×844
phone occupies 26% of the screen and reads as a banner, not as architecture.
This requires a second image crop per hero slide — budget for it in the shoot.

---

## Touch adaptations

Handled in one `@media (hover: none)` block:

- No image zoom on card hover.
- Team photos stay in colour (there is no hover to reveal them).
- Desktop dropdowns are removed entirely — they would need a first tap to open,
  which breaks the link.

Plus:
- Minimum touch target 44×44px (back-to-top, burger, dots, lightbox controls).
- Lightbox arrows relocate to the bottom corners below 700px, out of the
  thumb-drag zone.
- Swipe on hero and lightbox, 45px threshold.
- All scroll listeners are `{ passive: true }` — a non-passive listener blocks
  scrolling on mobile Safari and is the single most common cause of jank.

---

## Landscape phones

At 844×390 a `100svh` hero is fine, but `--section-y` (viewport-derived) gets
tight. If the practice's audience skews to landscape browsing, add:

```css
@media (max-height: 480px) and (orientation: landscape) {
  .hero { height: 100svh; min-height: 320px; }
  :root { --section-y: 40px; }
}
```

Not included by default — it is a real but uncommon case, and an unused media
query is a maintenance cost.

---

## Testing matrix

Test at these exact widths, in this order:

| Width | Device | Watch for |
|---|---|---|
| 1920 | Desktop | Grid caps at 1600, gutters don't sprawl |
| 1440 | MacBook Pro | Reference desktop layout |
| 1280 | Small laptop | Nav doesn't wrap |
| 1024 | iPad landscape | Still 3-up; nav still horizontal |
| 900 | **Nav switch** | The one-pixel test: 899 vs 900 |
| 834 | iPad Air portrait | 2-up grid, burger, sub-nav scrolls |
| 768 | iPad Mini | Same |
| 700 | **Column collapse** | 699 vs 700 |
| 430 | iPhone Pro Max | Portrait hero, 1-up |
| 390 | iPhone Pro | Primary phone target |
| 375 | iPhone SE / older | Gutters at 16px, nothing clipped |
| 320 | Galaxy Fold closed | **Nothing may overflow horizontally** |

At every width: no horizontal scroll, no text clipped, no image squashed, all
touch targets ≥ 44px.

---

## Performance on mobile

- `object-fit: cover` on every media element — never let the browser letterbox.
- Only the first hero slide is eager; the rest are lazy.
- Hero autoplay pauses when off-screen (IntersectionObserver) and when the tab is
  hidden (`visibilitychange`). Both matter for battery.
- Scroll handlers are rAF-throttled and passive.
- Only `opacity` and `transform` are animated — both compositor-only.

**Targets on a mid-range Android over 4G:** LCP < 2.5s, CLS < 0.05, INP < 200ms.

# 07 — Image Pipeline

You have photographs at 10–15 MB, 300 DPI, in whatever shape the camera produced.
The website needs them at 2400×1350, 72 DPI, under 320 KB, cropped to an exact
ratio. This does that, in bulk, without you opening Photoshop once.

---

## Install once

```bash
pip3 install --upgrade Pillow
```

That's the only dependency.

---

## Two ways to run it

### The control panel (recommended)

```bash
python3 image-prep/studio.py
```

A browser window opens at `http://localhost:8765`. You get:

- Every folder with photos waiting, and how many
- Which preset each folder will use, and what it produces
- Thumbnails of what's queued, and the name each file will be given
- **Preview** — shows the full plan without writing anything
- **Process** — does it, with a before/after table
- A **Rebuild the website now** button so you don't have to switch back
- A panel showing which slots are already filled on the live site

It runs entirely on your machine, talks to nothing, and stops when you close the
terminal. It is not deployed with the site.

### The terminal

```bash
python3 image-prep/process.py                 # everything in the inbox
python3 image-prep/process.py --dry-run       # show the plan, change nothing
python3 image-prep/process.py --only projects/13-riverside-house
python3 image-prep/process.py --anchor top    # override where it crops from
python3 image-prep/process.py --keep          # don't archive the originals
```

Same engine. The panel just calls it.

---

## Where photographs go

`image-prep/inbox/` mirrors `website/content/` exactly. Drop files into the
folder matching where they should appear:

```
image-prep/inbox/
├── _START-HERE.txt
├── home/
│   ├── hero/               homepage slideshow          → 2400×1350
│   └── hero-mobile/        the same slides, portrait   → 1200×1500
├── projects/
│   ├── _TEMPLATE-copy-me/  copy this for a new project
│   └── <NN-slug>/
│       ├── cover.jpg       grid thumbnail              → 1200×900
│       ├── hero.jpg        page banner                 → 2400×1350
│       └── gallery/        the photo sequence          → 2000×1333
├── about/
│   ├── principals/         portraits                   → 900×1125
│   └── team/               headshots                   → 700×700
└── news/                   news card images            → 1000×750
```

Every folder has a `_README.txt` stating exactly what it produces.

**Naming:** gallery and slideshow files are renamed `01.jpg`, `02.jpg`, … in
**alphabetical order**. So name your originals so they sort the way you want them
to appear: `01-approach.jpg`, `02-verandah.jpg`, `03-stair.jpg`. `cover.jpg` and
`hero.jpg` keep their names.

Accepted inputs: JPG, PNG, TIFF, WebP, BMP, HEIC.

---

## What happens to each file

1. **EXIF orientation applied, then all metadata stripped.** Phone photos are
   frequently stored sideways with a "rotate me" flag; this bakes the rotation
   in. Camera model, lens, and **GPS coordinates** are then removed — you do not
   want your clients' home addresses embedded in the images on your website.

2. **Colour mode normalised.** CMYK (from print work) and 16-bit files become
   8-bit RGB. PNGs with transparency are flattened onto white. A CMYK JPEG
   displays with inverted colours in some browsers, so this is not cosmetic.

3. **Cropped to the target ratio.** Never squashed. See "Cropping" below.

4. **Resized** to exact pixel dimensions with Lanczos resampling.

5. **Sharpened** slightly (unsharp mask, radius 0.8, 55%). Any downscale softens
   an image; this restores the edge definition that architectural photography
   depends on.

6. **Resolution set to 72 DPI.** For the record: DPI is metadata and has zero
   effect on how a browser displays an image — only pixel dimensions matter. It
   is set correctly anyway so the files are unambiguous if anyone inspects them.

7. **Compressed to fit the budget.** The encoder binary-searches JPEG quality to
   find the *highest* setting that still fits under the cap. A flat facade shot
   might land at q88; a detailed interior at q62. A single fixed quality would
   make one of them bloated and the other mushy.

   Output is **progressive JPEG** — it renders top-to-bottom as it downloads
   rather than appearing all at once, which feels faster on slow connections.

8. **Written** to `website/content/<matching path>/`.

9. **Original moved** to `image-prep/archive/<timestamp>/`. Nothing is destroyed.
   Use `--keep` to leave them in the inbox instead.

10. **`project.json` gallery lists updated** to match the files now on disk.
    Captions are preserved by position, so adding one photo doesn't wipe the
    captions you already wrote.

11. **A CSV log** is written to `image-prep/logs/`, recording every file's before
    and after size, the quality chosen, and any warning.

---

## Cropping

Turning a 3:2 photograph into a 16:9 banner means losing part of it. The `anchor`
setting decides which part.

| Anchor | Behaviour |
|---|---|
| `smart` | **Default.** Finds the region with the most detail and keeps that |
| `center` | Takes the middle |
| `top` | Keeps the top — default for portraits, so heads don't get cut |
| `bottom` | Keeps the bottom |

**How `smart` works:** the image is reduced to a small edge map, then the crop
window is slid across it and scored. The position with the most edge energy wins.
In architectural photography that reliably tracks the building rather than the
empty sky or the foreground paving — which is exactly where a centre crop tends
to fail.

It is a heuristic, not magic. If one particular image crops badly, run just that
folder with an explicit anchor:

```bash
python3 image-prep/process.py --only projects/13-riverside-house --anchor top
```

Or pre-crop that one file to roughly the right shape before dropping it in — the
processor will then have nothing to guess about.

---

## Presets

`image-prep/presets.json` holds the numbers.

```json
"gallery": {
  "label": "Project detail photo",
  "width": 2000, "height": 1333, "ratio": "3:2",
  "maxKB": 280
}
```

| Preset | Pixels | Ratio | Budget |
|---|---|---|---|
| `hero` | 2400×1350 | 16:9 | 320 KB |
| `hero-mobile` | 1200×1500 | 4:5 | 220 KB |
| `cover` | 1200×900 | 4:3 | 180 KB |
| `gallery` | 2000×1333 | 3:2 | 280 KB |
| `principal` | 900×1125 | 4:5 | 150 KB |
| `team` | 700×700 | 1:1 | 110 KB |
| `news` | 1000×750 | 4:3 | 150 KB |

> **If you change `width` or `height` here, you must change the matching entry in
> the `DIMS` table at the top of `tools/build.py`.** Those numbers are written
> into the HTML as `width` and `height` attributes, which is what reserves the
> right amount of space before the image loads. If the two disagree, the page
> jumps as it loads.

`maxKB` you can change freely. Raising it gives sharper images and a slower site;
lowering it does the reverse. The defaults target a homepage under 1.2 MB.

---

## Reading the output

```
SOURCE                                  PRESET      BEFORE    AFTER   Q  DESTINATION
--------------------------------------------------------------------------------------
projects/03-x/gallery/DSC_0912.jpg      gallery    1489KB    176KB   88  projects/03-x/gallery/01.jpg
home/hero/scan_A.tif                    hero      68360KB    226KB   84  home/hero/01.jpg

74.1 MB  ->  1.1 MB   (99% smaller)
```

**Warnings you might see:**

- `original only 1400px wide, needed 2400 — not upscaled`
  The source is too small. It has been stretched to fit and will look soft. Get a
  larger original. This is the one warning worth acting on every time.

- `over budget even at q55`
  An unusually detailed image couldn't be squeezed under the cap without
  visible damage. Either accept it (a single 400 KB image is not a disaster) or
  raise that preset's `maxKB`.

- `no matching preset — check the folder name`
  The file is in a folder the router doesn't recognise — usually loose in
  `inbox/` rather than in a subfolder, or a project slug that's misspelled. It
  was ignored, not processed.

---

## After processing

```bash
python3 tools/build.py
```

Nothing appears on the site until you do this. The control panel has a button
for it.

---

## Things worth knowing

**Re-running is safe.** Processing the same folder again just overwrites the
outputs. The inbox empties as it goes, so a second run with an empty inbox does
nothing.

**Everything is reversible.** Originals go to `image-prep/archive/<timestamp>/`,
never deleted. If a batch comes out wrong, copy them back from the archive and
re-run with different settings.

**`image-prep/` is not uploaded.** Only the `website/` folder goes to Hostinger.
Your originals and archive stay on your machine.

**Realistic throughput:** roughly 1–3 seconds per image. A 200-photograph batch
takes a few minutes. Leave it running.

---

## Next step, when you're ready

The biggest remaining performance win is serving **AVIF and WebP** alongside
JPEG, which typically halves the bytes again. That needs `<picture>` elements in
the HTML and extra encoders installed. It is a real improvement but it is not
required to launch — there's a ready-made Claude Code prompt for it in
`08-DEPLOY.md`.

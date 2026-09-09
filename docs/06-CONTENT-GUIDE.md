# 06 — Content Guide

How to replace everything in the site with your own material. This is the
document to keep open while you work.

You do not need to know HTML. You edit **text files** and **image folders**, then
run one command.

---

## The mental model

```
   website/content/          ←  you edit THIS
        │
        │   python3 tools/build.py
        ▼
   website/*.html            ←  generated. never edit by hand.
        │
        │   upload to Hostinger
        ▼
   your live website
```

Two kinds of thing live in `website/content/`:

- **`.json` files** — all the words.
- **image folders** — all the pictures.

Everything you can see on the site comes from one of those two. Nothing else.

---

## Before you start: install two things

**1. A text editor that understands JSON.**
Download [VS Code](https://code.visualstudio.com) (free). It will underline a
mistake in red the moment you make one, which saves a lot of confusion later.
TextEdit and Notepad will work but won't warn you.

**2. Python with Pillow**, for the image processor:

```bash
pip3 install --upgrade Pillow
```

macOS and most Linux systems already have Python. On Windows install it from
[python.org](https://python.org) and tick "Add Python to PATH".

---

## JSON: the five rules

JSON is fussy but simple. Almost every error is one of these:

1. Text goes in **double quotes**: `"Bengaluru"` — never `'Bengaluru'`.
2. Items in a list are separated by **commas**, and the **last one has no comma**.
3. Don't delete the `{ }` or `[ ]` brackets.
4. To use a double quote inside text, escape it: `"the \"Chhaaya\" house"`.
5. `_comment` fields are notes to yourself. They're ignored. Leave or delete them.

If the build says *"is not valid JSON — line 34"*, go to line 34, and look at the
line **above** it too. It's nearly always a missing or extra comma.

---

## 1 · Brand, contact details, navigation

**File:** `website/content/site.json`

| Field | Shows up |
|---|---|
| `brand` | Logo, page titles, footer |
| `tagline` | Under the logo |
| `domain` | Sitemap and social share links — set this to your real domain |
| `email`, `phone`, `phoneAlt` | Contact page, footer, mobile menu |
| `address` | Contact page. It's a list — one line per line of the address |
| `enquiryEmail`, `careersEmail`, `careersNote` | Contact page |
| `copyrightYear` | Footer |
| `social` | Footer links. Delete an entry to remove that link |
| `categories` | The project filter tabs **and** the Projects dropdown |
| `home` | Everything on the homepage that is text |

### Renaming or changing categories

Change the `label` freely — it's just what people see:

```json
{ "slug": "residential", "label": "Houses" }
```

Change the `slug` only if you also change `"category"` in every `project.json`
that uses it. The slug is the invisible link between a project and its tab.
Keep `"slug": "all"` — it's the "show everything" tab.

To add a category, add an entry here **and** set that slug as the `category` on
at least one project. A tab with no projects behind it looks broken.

---

## 2 · The About page

**File:** `website/content/about.json`
**Photos:** `website/content/about/principals/` and `website/content/about/team/`

Four sections: `firm`, `philosophy`, `principals`, `team`.

`paragraphs` is a list. Each entry becomes one paragraph on the page. Add or
remove entries freely:

```json
"paragraphs": [
  "First paragraph.",
  "Second paragraph.",
  "Third paragraph."
]
```

For team members, the `photo` field points at a file inside
`website/content/about/`. If you have six people instead of eight, delete two
entries from the `team` list and delete the two image files.

**Write this section properly.** It is what a prospective client actually reads.
Do not let it be the last thing you do.

---

## 3 · News, Press, Awards, Books

**File:** `website/content/news.json`
**Photos:** `website/content/news/`

**`highlights`** — the cards on the News page. Each has a photo, a date, a link
and some text. The `<strong>` tags around project names and award names are what
create the visual hierarchy — keep using them:

```json
{
  "photo": "01.jpg",
  "date": "March 2026",
  "url": "https://example.com/the-article",
  "text": "<strong>Villa 106</strong> wins <strong>House of the Year</strong>."
}
```

Set `"url": "#"` if there's nothing to link to.

**`press`, `awards`, `books`** — plain lists, grouped under a heading. `group` is
the heading (a year for awards, "International"/"Domestic" for press):

```json
{ "group": "2026", "items": [
    "<strong>Some Award</strong> &mdash; Winner, Best House.",
    "<strong>Another Award</strong> &mdash; Finalist."
]}
```

`&mdash;` is a long dash. `&amp;` is an ampersand. You need those written that
way, not as the raw characters.

---

## 4 · Projects — the important one

**One folder per project.** The folder *is* the project. There is no master list
to keep in sync.

```
website/content/projects/
├── 01-lorem-ipsum-house/
│   ├── project.json
│   ├── cover.jpg          ← the grid thumbnail    1200×900
│   ├── hero.jpg           ← the page banner       2400×1350
│   └── gallery/
│       ├── 01.jpg         ← the photo sequence    2000×1333
│       ├── 02.jpg
│       └── 03.jpg
└── 02-dolor-sit-villa/
    └── …
```

### Folder naming

`NN-slug` — a two-digit number, a hyphen, then lowercase words joined by hyphens.

- The **number** controls grid order. `01` appears first.
- The **rest** becomes the web address: `13-riverside-house` →
  `project-13-riverside-house.html`

Lowercase, hyphens, no spaces, no accents, no `&`.

### project.json, field by field

| Field | What it does |
|---|---|
| `title` | Shown on the card and as the page heading |
| `location`, `year` | The caption under the card, and the page subtitle |
| `category` | Must match a `slug` in `site.json` — this is what the filter uses |
| `featured` | `true` puts it in the homepage "Selected Work" grid (first 6 win) |
| `order` | Grid position. Lower first. Usually matches the folder number |
| `intro` | A list of paragraphs. **Write 3–14.** This is the project description |
| `pullQuote` | One sentence repeated large mid-page. Lift it from `intro` |
| `pullQuoteAfter` | Show it after this many gallery images. `0` = don't show |
| `gallery` | The photo sequence — see below |
| `credits` | The table at the bottom. Add or remove rows freely |

### The gallery list

```json
"gallery": [
  { "file": "gallery/01.jpg", "caption": "The south verandah", "layout": "full" },
  { "file": "gallery/02.jpg", "caption": "", "layout": "pair" },
  { "file": "gallery/03.jpg", "caption": "", "layout": "pair" }
]
```

- `layout: "full"` — full width of the screen, on its own.
- `layout: "pair"` — half width. Two consecutive `pair` entries sit side by side.
- `caption` — optional. Leave `""` for none.

**Rhythm rule:** don't put more than two `full` images in a row without a `pair`
or the pull quote between them. Monotony is how this page template fails.

The image processor rewrites this list automatically to match the files actually
on disk, keeping your captions. So you can add a photo, re-run it, and only need
to set the `layout` for the new one.

### Adding a new project — the whole procedure

```bash
# 1. Copy an existing project folder and rename it
cd website/content/projects
cp -R 01-lorem-ipsum-house 13-riverside-house

# 2. Put your original photographs in the inbox instead
#    image-prep/inbox/projects/13-riverside-house/cover.jpg
#    image-prep/inbox/projects/13-riverside-house/hero.jpg
#    image-prep/inbox/projects/13-riverside-house/gallery/*.jpg

# 3. Resize them all
python3 image-prep/process.py

# 4. Edit website/content/projects/13-riverside-house/project.json

# 5. Rebuild
python3 tools/build.py
```

There is a ready-made template at
`image-prep/inbox/projects/_TEMPLATE-copy-me/` with instructions inside.

> **Watch for leftovers.** If you copy an existing project folder and the old one
> had eight gallery photos while your new one has four, the old images 05–08 are
> still sitting there and will appear on your new page. Delete every file inside
> the copied `gallery/` folder before you start, then let the processor put your
> own photographs in. The processor overwrites `01.jpg`–`04.jpg` but has no way
> to know that `05.jpg` was never meant to be there.

### Deleting a project

Delete its folder from `website/content/projects/`, then run the build. The old
`project-*.html` file is turned into a redirect to the projects index, so any
existing link to it still lands somewhere sensible rather than on a 404.

---

## 5 · Images

Never resize by hand. Put originals in `image-prep/inbox/` and run the processor.
It handles resolution, cropping, compression and renaming. Full detail in
`07-IMAGE-PIPELINE.md`.

Quick reference for what each slot becomes:

| Where | Final size | Ratio | Budget |
|---|---|---|---|
| `home/hero/` | 2400×1350 | 16:9 | 320 KB |
| `home/hero-mobile/` | 1200×1500 | 4:5 | 220 KB |
| `projects/*/cover.jpg` | 1200×900 | 4:3 | 180 KB |
| `projects/*/hero.jpg` | 2400×1350 | 16:9 | 320 KB |
| `projects/*/gallery/` | 2000×1333 | 3:2 | 280 KB |
| `about/principals/` | 900×1125 | 4:5 | 150 KB |
| `about/team/` | 700×700 | 1:1 | 110 KB |
| `news/` | 1000×750 | 4:3 | 150 KB |

---

## "I don't have all the content yet"

You almost certainly don't, and that's normal. Handle it like this:

### You have fewer projects than the 12 placeholders

Delete the folders you don't need. **Six good projects beat twelve thin ones.**
An architecture practice is judged on the quality of what it shows, not the
count. Keep the numbering contiguous (`01`…`06`) so the grid order stays obvious.

### You have no photograph for a slot

Leave the placeholder. It is a neutral grey block — it reads as "coming soon"
rather than as broken. Replace it when the photograph exists. Never ship a
stretched or low-resolution image; a placeholder is less damaging than a bad
photo.

### You don't have project descriptions written

Put a single honest sentence in `intro` for now:

```json
"intro": ["A 640 sqm private residence in Bengaluru, completed in 2025."]
```

That is far better than lorem ipsum, which looks like an unfinished site to
anyone who reads it. Fill in the full description later.

### You don't have team headshots

Delete the `team` entries from `about.json` and delete the section. A practice
with two principals and no team grid looks deliberate. A team grid full of grey
squares looks unfinished.

### You're missing the address or phone number

Fill in what you have. Remove the `<br>` line from `address` if it's shorter.
Never leave `+91 00 0000 0000` on a live site — delete the whole Telephone block
from `contact.json` instead if the number isn't ready.

### General principle

**Ship less, complete.** Every placeholder you leave visible costs more
credibility than the missing content would have earned. Cut the section.

---

## Should you keep building here, or move to Claude Code?

Honest answer, and it depends on what you're doing:

### Stay in this interface (Cowork) when
- You're changing text, swapping images, adding or removing projects.
- You want something explained or reviewed.
- You're doing anything you'd describe in a sentence.

This is the right tool for running the site. The JSON-plus-folders structure was
built specifically so that content work never requires a developer.

### Move to Claude Code when
- You want real design changes across many files at once.
- You're adding a whole new page type or section.
- You want the responsive-image pipeline (`<picture>` with AVIF/WebP).
- You want to convert to a CMS.

Claude Code sits in your terminal, can run the build and see the errors, and can
iterate over many files quickly. `08-DEPLOY.md` has ready-made prompts for the
larger jobs.

### One thing to be aware of

This session has a **conversation length limit**. If you're planning a long
back-and-forth — writing all twelve project descriptions, say — do it in
batches, and after each batch ask me to save the result to the JSON files. The
files persist; the conversation doesn't.

---

## Every command, in one place

```bash
# See the site locally (needed — the filter reads the URL)
cd website && python3 -m http.server 8000
#   → http://localhost:8000

# Process new photographs
python3 image-prep/process.py                   # everything in the inbox
python3 image-prep/process.py --dry-run         # show the plan only
python3 image-prep/process.py --only projects/13-riverside-house
python3 image-prep/studio.py                    # visual control panel

# Rebuild the HTML after any content change
python3 tools/build.py

# Check nothing is broken
python3 tools/validate.py
```

**After every content change, run `tools/build.py`.** Nothing appears on the site
until you do.

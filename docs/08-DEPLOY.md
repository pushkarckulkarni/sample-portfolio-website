# 08 — Deploying to Hostinger

The short version: **upload the contents of `website/` into `public_html/`.**
That folder is completely self-contained — HTML, CSS, JS, and every image.

---

## Before the first upload

Work through these. Each one is a thing visitors will notice if it's missing.

- [ ] Set `"domain"` in `website/content/site.json` to your real domain
      (no trailing slash). It feeds the sitemap and social share cards.
- [ ] Replace the lorem ipsum in `site.json`, `about.json`, `news.json` and every
      `project.json`. See `06-CONTENT-GUIDE.md`.
- [ ] Replace the placeholder photographs. See `07-IMAGE-PIPELINE.md`.
- [ ] Add the fonts (below).
- [ ] Add a favicon set (below).
- [ ] Run `python3 tools/build.py`
- [ ] Run `python3 tools/validate.py` — it must say **ALL PASS**.

---

## Fonts

`website/assets/fonts/` is currently empty, so the site falls back to Futura /
Century Gothic / system-ui. That looks close, but not identical.

1. Download **Jost** and **Inter** from Google Fonts.
2. Subset them to Latin (use [glyphhanger](https://github.com/zachleat/glyphhanger)
   or [Fontsquirrel](https://www.fontsquirrel.com/tools/webfont-generator)).
   A subsetted weight is 15–25 KB; the full family is 300 KB+.
3. Save them with exactly these names:

```
website/assets/fonts/
  jost-300.woff2   jost-400.woff2   jost-500.woff2
  inter-300.woff2  inter-400.woff2
```

The `@font-face` rules are already written in `assets/css/base.css`. Nothing else
to do.

**Why self-host rather than link to Google Fonts:** on Indian mobile networks a
Google Fonts round-trip costs 200–400 ms before any text renders. A local woff2
costs nothing. It also avoids a third-party request you'd otherwise have to
mention in a privacy policy.

---

## Favicons

Generate a set at [realfavicongenerator.net](https://realfavicongenerator.net)
and drop these into `website/`:

```
favicon.ico
apple-touch-icon.png     (180×180)
favicon-32x32.png
favicon-16x16.png
site.webmanifest
```

Then add this to the `head()` function in `tools/build.py`, just above the
stylesheet links, and rebuild:

```html
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
```

---

## Uploading

### Option A — hPanel File Manager

1. hPanel → **Files → File Manager**
2. Open `public_html/`
3. Delete Hostinger's default `index.html`
4. Upload the **contents** of `website/` — not the folder itself. You should end
   up with `public_html/index.html`, not `public_html/website/index.html`.
5. **Enable Settings → Show hidden files**, then confirm `.htaccess` is there.
   File Manager hides dotfiles by default and it is very easy to miss.

Zipping `website/` first, uploading the single zip, and extracting it in place is
much faster than uploading a few hundred images individually.

### Option B — FTP (better for repeat deploys)

Credentials: hPanel → **Files → FTP Accounts**

```
Host: ftp.yourdomain.com
Port: 21
Remote directory: /public_html
```

Use FileZilla, or from the terminal:

```bash
lftp -u USERNAME,PASSWORD ftp.yourdomain.com \
     -e "mirror -R --delete --verbose website/ /public_html; quit"
```

`--delete` removes files on the server that no longer exist locally, which keeps
old project pages from lingering. Leave it off for your first upload until you're
confident the paths are right.

---

## Do not upload

| Folder | Why |
|---|---|
| `image-prep/` | Your originals and archive. Large, and nobody needs them |
| `docs/` | Internal documentation |
| `tools/` | Build scripts — they run on your machine, not the server |
| `CLAUDE.md`, `README.md` | Internal |

Only `website/` goes up. Everything else stays with you.

---

## Immediately after uploading

- [ ] hPanel → **SSL** → install the free Let's Encrypt certificate
- [ ] Turn on **Force HTTPS**
- [ ] hPanel → **Performance → LiteSpeed Cache** → enable
- [ ] Visit `yourdomain.com` — the homepage slideshow should run
- [ ] Visit `yourdomain.com/about` (no `.html`) — clean URLs are working
- [ ] Visit `yourdomain.com/nonsense` — your 404 page, not Hostinger's
- [ ] Check `http://` and `www.` both redirect to the canonical `https://`
- [ ] Open it on a real phone. Not a simulator
- [ ] Run [PageSpeed Insights](https://pagespeed.web.dev) on mobile

Then work through `09-QC-CHECKLIST.md` Parts C and D.

---

## What `.htaccess` is doing

It's already written. For reference:

- Forces HTTPS and strips `www.`
- **Clean URLs** — `/about` serves `about.html`
- Custom 404
- Gzip compression on HTML, CSS, JS
- Cache headers — images and fonts for a year, HTML never
- Security headers — `X-Content-Type-Options`, `Referrer-Policy`,
  `X-Frame-Options`, HSTS
- Directory listing disabled

If the site 500s immediately after upload, `.htaccess` is the first suspect —
rename it to `.htaccess.bak` and reload. If that fixes it, your Hostinger plan is
missing one of the Apache modules; comment out the `<IfModule>` blocks one at a
time to find which.

---

## Updating a live site

```bash
# 1. change content
# 2. process any new photographs
python3 image-prep/process.py
# 3. rebuild
python3 tools/build.py
# 4. verify
python3 tools/validate.py
# 5. upload
```

For a text-only change you only need to re-upload the affected `.html` files.
For a new project, upload the new `project-*.html`, the updated `index.html` and
`projects.html`, and the new folder under `content/projects/`.

Keep a copy of the whole project folder on your machine — it is the master.
The server is just a copy.

---

## Prompts for Claude Code

Run these from the project root. Each is self-contained.

### Responsive images (AVIF + WebP)
```
Read CLAUDE.md and docs/07-IMAGE-PIPELINE.md first.

Extend image-prep/process.py to also emit AVIF and WebP alongside each JPEG,
and update tools/build.py so its img() helper produces a <picture> element with
AVIF and WebP sources and the JPEG as fallback.

Add srcset/sizes for these widths:
  cover:   400/800/1200w   sizes="(max-width:699px) 100vw, (max-width:899px) 50vw, 33vw"
  hero:    800/1600/2400w  sizes="100vw"
  gallery: 800/1400/2000w  sizes="100vw"

Keep the width/height attributes on the <img> — they are what keep CLS at zero.
Do not change presets.json dimensions without changing DIMS in build.py to match.
Run tools/validate.py when done.
```

### Mobile hero crops
```
The homepage hero currently uses the same 16:9 images at every size. Make it use
content/home/hero-mobile/*.jpg (4:5 portrait) below 700px via a <picture> element
with a media query source.

Match files by number: hero/01.jpg pairs with hero-mobile/01.jpg. If a mobile
crop is missing, fall back to the landscape file rather than breaking.
```

### Accessibility audit
```
Audit every page in website/ against WCAG 2.2 AA and fix what you find.

Check: contrast for --c-ink-mute in each context it's used; keyboard access to
the nav dropdowns, hero slider and lightbox; focus trap and restoration in the
mobile menu and lightbox; the aria-live count on the project filter; heading
order; alt text (empty for decorative, descriptive for content).

Do not change the visual design. Report what changed and why.
```

### Contact form
```
Add a contact form to contact.html. Hostinger shared hosting supports PHP, so
use a small PHP handler with server-side validation, a honeypot field, and a
mailto target read from content/site.json.

Style it with existing tokens only — no new CSS variables. It must work without
JavaScript. Add the markup generation to page_contact() in tools/build.py, not
by hand-editing the HTML.
```

### Move to a CMS (only when you've outgrown editing JSON)
```
Convert this to Astro while preserving the exact rendered HTML and all existing
CSS unchanged.

- Header, footer and nav become components
- content/projects/*/project.json becomes a content collection
- Output stays fully static, deployed to Hostinger over FTP
- The rendered DOM should be comparable to the current build

Do not restyle anything.
```

---

## When to add a CMS

Not yet. At a dozen projects updated a few times a year, editing JSON is faster
than maintaining a CMS. Revisit when **any** of these is true:

- More than one person needs to publish
- Updates happen more than monthly
- The project count passes ~40
- Someone non-technical needs to add a project with no help at all

Then: **Astro** (static output, deploys to Hostinger unchanged) or **Decap CMS**
(git-backed, free, no server). Not WordPress — it is what made the reference site
slow.

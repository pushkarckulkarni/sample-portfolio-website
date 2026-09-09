#!/usr/bin/env python3
"""
================================================================================
SAMPLE PORTFOLIO — BULK IMAGE PROCESSOR
================================================================================

WHAT IT DOES
    Takes your full-size photographs (10-15 MB straight off a camera or from a
    photographer) and turns them into web images the site can actually serve:

      1. Reads and applies the EXIF orientation flag, then strips all metadata
         (camera model, GPS, copyright) so nothing private ships to the web.
      2. Converts CMYK / 16-bit / PNG-with-transparency to plain 8-bit RGB.
      3. Crops to the exact aspect ratio the page slot needs — no squashing.
      4. Resizes to the exact pixel dimensions the HTML declares.
      5. Sets the resolution flag to 72 DPI.
      6. Searches for the highest JPEG quality that still fits the size budget
         (roughly 110-320 KB depending on the slot).

    Output goes straight into  website/content/  under the matching path, so the
    website updates the moment you re-run tools/build.py.

USAGE
    python3 image-prep/process.py                 process everything in inbox/
    python3 image-prep/process.py --dry-run       show the plan, change nothing
    python3 image-prep/process.py --only projects/03-consectetur-clubhouse
    python3 image-prep/process.py --anchor top    override the crop anchor
    python3 image-prep/process.py --keep          don't move originals to archive/

WHERE TO PUT YOUR PHOTOS
    image-prep/inbox/home/hero/*.jpg
    image-prep/inbox/home/hero-mobile/*.jpg
    image-prep/inbox/projects/<slug>/cover.jpg
    image-prep/inbox/projects/<slug>/hero.jpg
    image-prep/inbox/projects/<slug>/gallery/*.jpg
    image-prep/inbox/about/principals/*.jpg
    image-prep/inbox/about/team/*.jpg
    image-prep/inbox/news/*.jpg

    Gallery files are renamed to 01.jpg, 02.jpg … in alphabetical order, so name
    your originals so they sort the way you want them to appear on the page.

REQUIREMENTS
    pip3 install --upgrade Pillow
================================================================================
"""

import os, sys, json, glob, shutil, fnmatch, argparse, io, csv, datetime

try:
    from PIL import Image, ImageOps, ImageFilter
except ImportError:
    sys.exit("ERROR: Pillow is not installed.\n       Run:  pip3 install --upgrade Pillow")

Image.MAX_IMAGE_PIXELS = None          # allow very large scans

HERE     = os.path.dirname(os.path.abspath(__file__))
ROOT     = os.path.normpath(os.path.join(HERE, ".."))
INBOX    = os.path.join(HERE, "inbox")
ARCHIVE  = os.path.join(HERE, "archive")
LOGS     = os.path.join(HERE, "logs")
CONTENT  = os.path.join(ROOT, "website", "content")
PRESETS  = os.path.join(HERE, "presets.json")

EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp", ".heic", ".heif")


# ----------------------------------------------------------------- config ---

def load_presets():
    with open(PRESETS, encoding="utf-8") as f:
        cfg = json.load(f)
    d = cfg["defaults"]
    for name, p in cfg["presets"].items():
        for k, v in d.items():
            p.setdefault(k, v)
        p["name"] = name
    return cfg


def route(rel, cfg):
    """Map an inbox-relative path to (preset, output dir, rename mode)."""
    rel = rel.replace(os.sep, "/")
    for r in cfg["routing"]:
        if fnmatch.fnmatch(rel, r["match"]):
            parts = rel.split("/")
            out = r["out"]
            # {p1} = the second path segment, i.e. the project slug
            if "{p1}" in out:
                out = out.replace("{p1}", parts[1])
            return cfg["presets"][r["preset"]], out, r["rename"]
    return None, None, None


# ------------------------------------------------------------ image logic ---

def smart_offset(im, tw, th):
    """
    Choose where to crop from, instead of always taking the middle.

    Architecture photos are frequently composed with the building high in the
    frame and a lot of empty foreground, so a naive centre crop cuts the roof
    off. This slides the crop window across the image and keeps the position
    with the most edge detail, which in practice tracks the building.
    """
    w, h = im.size
    src_ratio, dst_ratio = w / h, tw / th

    # Work on a small greyscale edge map — fast, and detail survives downscaling
    small = im.convert("L").resize((160, 160)).filter(ImageFilter.FIND_EDGES)
    px = small.load()

    if abs(src_ratio - dst_ratio) < 0.001:
        return 0.5

    if src_ratio > dst_ratio:
        # too wide → we slide horizontally, so score vertical strips
        scores = [sum(px[x, y] for y in range(160)) for x in range(160)]
        keep = int(160 * (dst_ratio / src_ratio))
    else:
        # too tall → we slide vertically, so score horizontal strips
        scores = [sum(px[x, y] for x in range(160)) for y in range(160)]
        keep = int(160 * (src_ratio / dst_ratio))

    keep = max(1, min(160, keep))
    best_i, best_v = 0, -1
    run = sum(scores[:keep])
    best_v, best_i = run, 0
    for i in range(1, 160 - keep + 1):
        run += scores[i + keep - 1] - scores[i - 1]
        if run > best_v:
            best_v, best_i = run, i

    centre = (best_i + keep / 2) / 160.0
    return min(max(centre, 0.0), 1.0)


def crop_to_ratio(im, tw, th, anchor):
    """Crop (never squash) to the target aspect ratio."""
    w, h = im.size
    src, dst = w / h, tw / th
    if abs(src - dst) < 0.0005:
        return im

    if anchor == "smart":
        pos = smart_offset(im, tw, th)
    else:
        pos = {"center": .5, "centre": .5, "top": 0.0, "bottom": 1.0,
               "left": 0.0, "right": 1.0}.get(anchor, .5)

    if src > dst:                       # too wide → trim the sides
        new_w = int(round(h * dst))
        max_x = w - new_w
        x = int(round(max_x * (pos if anchor in ("smart", "left", "right", "center", "centre") else .5)))
        x = max(0, min(max_x, x))
        return im.crop((x, 0, x + new_w, h))
    else:                               # too tall → trim top/bottom
        new_h = int(round(w / dst))
        max_y = h - new_h
        y = int(round(max_y * pos))
        y = max(0, min(max_y, y))
        return im.crop((0, y, w, y + new_h))


def encode_to_budget(im, max_kb, q_lo, q_hi, dpi):
    """
    Binary-search JPEG quality for the best image that fits the budget.

    We want the *highest* quality under the cap, not a fixed quality — a flat
    facade shot might fit at q=88 while a detailed interior needs q=62, and
    hard-coding one number would make one of them either bloated or mushy.
    """
    best = None
    lo, hi = q_lo, q_hi
    while lo <= hi:
        mid = (lo + hi) // 2
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=mid, optimize=True,
                progressive=True, subsampling=2, dpi=(dpi, dpi))
        size = buf.tell()
        if size <= max_kb * 1024:
            best = (buf.getvalue(), mid, size)
            lo = mid + 1                # try to do better
        else:
            hi = mid - 1

    if best is None:                    # even the floor quality is too big
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q_lo, optimize=True,
                progressive=True, subsampling=2, dpi=(dpi, dpi))
        best = (buf.getvalue(), q_lo, buf.tell())
    return best


def process_one(src_path, preset, out_dir, out_name, dry=False, anchor_override=None):
    """Returns a dict describing what happened — used by both CLI and GUI."""
    before = os.path.getsize(src_path)
    rec = {"src": src_path, "beforeKB": round(before / 1024),
           "preset": preset["name"], "ok": False, "note": ""}

    try:
        im = Image.open(src_path)
        rec["srcSize"] = f"{im.size[0]}x{im.size[1]}"
        rec["srcDPI"]  = im.info.get("dpi", (72, 72))[0]
    except Exception as e:
        rec["note"] = f"cannot open ({e})"
        return rec

    dst_rel = f"{out_dir}/{out_name}"
    rec["dst"] = dst_rel
    if dry:
        rec["ok"] = True
        rec["note"] = "dry run"
        return rec

    try:
        im = ImageOps.exif_transpose(im)            # honour camera rotation

        # Flatten anything with transparency onto white, and normalise mode.
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            im = bg
        elif im.mode != "RGB":
            im = im.convert("RGB")                  # CMYK, I;16, L, etc.

        tw, th = preset["width"], preset["height"]
        im = crop_to_ratio(im, tw, th, anchor_override or preset.get("anchor", "smart"))

        # Only ever downscale. Upscaling a small original just makes it soft.
        if im.size[0] > tw:
            im = im.resize((tw, th), Image.LANCZOS)
        else:
            rec["note"] = f"original only {im.size[0]}px wide, needed {tw} — not upscaled"
            im = im.resize((tw, th), Image.LANCZOS)

        im = im.filter(ImageFilter.UnsharpMask(radius=0.8, percent=55, threshold=3))

        data, q, size = encode_to_budget(
            im, preset["maxKB"], preset["minQuality"], preset["maxQuality"], preset["dpi"])

        full_out = os.path.join(CONTENT, out_dir)
        os.makedirs(full_out, exist_ok=True)
        with open(os.path.join(full_out, out_name), "wb") as f:
            f.write(data)

        rec.update(ok=True, afterKB=round(size / 1024), quality=q,
                   outSize=f"{tw}x{th}",
                   saved=f"{100 - round(size / before * 100)}%" if before else "-")
        if size > preset["maxKB"] * 1024:
            rec["note"] = (rec["note"] + " | " if rec["note"] else "") + \
                          f"over budget even at q{q}"
    except Exception as e:
        rec["note"] = f"failed ({e})"
    return rec


# ---------------------------------------------------------------- scanning --

def scan(cfg, only=None):
    """Build the work plan. Gallery/sequence folders are numbered in sort order."""
    jobs, groups = [], {}
    for path in sorted(glob.glob(os.path.join(INBOX, "**", "*"), recursive=True)):
        if not os.path.isfile(path):
            continue
        if not path.lower().endswith(EXT):
            continue
        rel = os.path.relpath(path, INBOX).replace(os.sep, "/")
        if only and not rel.startswith(only.rstrip("/")):
            continue
        preset, out, mode = route(rel, cfg)
        if preset is None:
            jobs.append({"rel": rel, "skip": "no matching preset — check the folder name"})
            continue
        groups.setdefault((out, mode, preset["name"]), []).append((rel, path))

    for (out, mode, pname), files in sorted(groups.items()):
        files.sort(key=lambda t: t[0].lower())
        for i, (rel, path) in enumerate(files, 1):
            if mode == "seq":
                name = f"{i:02d}.jpg"
            elif mode in ("cover", "hero"):
                name = f"{mode}.jpg"
            else:
                name = os.path.splitext(os.path.basename(path))[0].lower() + ".jpg"
            jobs.append({"rel": rel, "path": path, "preset": cfg["presets"][pname],
                         "out": out, "name": name})
    return jobs


def sync_project_json(cfg):
    """
    After processing, make each project.json's gallery list match the files that
    are actually on disk. Captions are preserved by position, so re-running the
    processor after adding one photo doesn't wipe the captions you wrote.
    """
    changed = []
    for pj in sorted(glob.glob(os.path.join(CONTENT, "projects", "*", "project.json"))):
        folder = os.path.dirname(pj)
        files = sorted(os.path.basename(f) for f in
                       glob.glob(os.path.join(folder, "gallery", "*.jpg")))
        if not files:
            continue
        with open(pj, encoding="utf-8") as f:
            d = json.load(f)
        old = {g["file"]: g for g in d.get("gallery", [])}
        new = []
        for i, fn in enumerate(files):
            key = f"gallery/{fn}"
            prev = old.get(key, {})
            new.append({"file": key,
                        "caption": prev.get("caption", ""),
                        "layout": prev.get("layout", "full" if i % 3 == 0 else "pair")})
        if new != d.get("gallery"):
            d["gallery"] = new
            with open(pj, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2)
            changed.append(os.path.basename(folder))
    return changed


def write_log(records):
    os.makedirs(LOGS, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    p = os.path.join(LOGS, f"run-{stamp}.csv")
    cols = ["src", "dst", "preset", "srcSize", "outSize", "srcDPI",
            "beforeKB", "afterKB", "saved", "quality", "ok", "note"]
    with open(p, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        wr.writeheader()
        for r in records:
            wr.writerow(r)
    return p


# -------------------------------------------------------------------- main --

def main():
    ap = argparse.ArgumentParser(description="Bulk-prepare photographs for the website.")
    ap.add_argument("--dry-run", action="store_true", help="show the plan, change nothing")
    ap.add_argument("--only", help="limit to one inbox subfolder, e.g. projects/03-x")
    ap.add_argument("--anchor", choices=["smart", "center", "top", "bottom", "left", "right"],
                    help="override the crop anchor for this run")
    ap.add_argument("--keep", action="store_true", help="leave originals in inbox/")
    args = ap.parse_args()

    cfg = load_presets()
    jobs = scan(cfg, args.only)
    todo = [j for j in jobs if "skip" not in j]
    skipped = [j for j in jobs if "skip" in j]

    if skipped:
        print("\nSKIPPED (not in any known folder):")
        for s in skipped:
            print(f"  {s['rel']}  — {s['skip']}")

    if not todo:
        print("\nNothing to process.")
        print(f"Put your photographs in: {INBOX}")
        print("Folder layout is described at the top of this file.\n")
        return

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}{len(todo)} image(s) to process\n")
    print(f"{'SOURCE':<44} {'PRESET':<12} {'BEFORE':>8} {'AFTER':>8} {'Q':>3}  DESTINATION")
    print("-" * 118)

    records, total_before, total_after = [], 0, 0
    for j in todo:
        r = process_one(j["path"], j["preset"], j["out"], j["name"],
                        dry=args.dry_run, anchor_override=args.anchor)
        records.append(r)
        total_before += r.get("beforeKB", 0)
        total_after  += r.get("afterKB", 0)
        print(f"{j['rel'][:43]:<44} {r['preset']:<12} "
              f"{str(r.get('beforeKB','?'))+'KB':>8} "
              f"{str(r.get('afterKB','-'))+'KB':>8} "
              f"{r.get('quality','-'):>3}  {r.get('dst','')}"
              + (f"   ⚠ {r['note']}" if r.get("note") and r["note"] != "dry run" else ""))

    if not args.dry_run:
        changed = sync_project_json(cfg)
        if changed:
            print(f"\nUpdated gallery lists in project.json for: {', '.join(changed)}")

        if not args.keep:
            os.makedirs(ARCHIVE, exist_ok=True)
            stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            moved = 0
            for j in todo:
                dest = os.path.join(ARCHIVE, stamp, j["rel"])
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                try:
                    shutil.move(j["path"], dest)
                    moved += 1
                except Exception:
                    pass
            if moved:
                print(f"Moved {moved} original(s) to archive/{stamp}/ "
                      f"(use --keep to leave them in inbox/)")

        log = write_log(records)
        pct = 100 - round(total_after / total_before * 100) if total_before else 0
        print(f"\n{total_before/1024:.1f} MB  ->  {total_after/1024:.1f} MB   ({pct}% smaller)")
        print(f"Log: {os.path.relpath(log, ROOT)}")
        print("\nNext:  python3 tools/build.py\n")
    else:
        print("\nDry run — nothing was written.\n")


if __name__ == "__main__":
    main()

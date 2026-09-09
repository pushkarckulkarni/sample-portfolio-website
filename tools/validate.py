#!/usr/bin/env python3
"""
================================================================================
SAMPLE PORTFOLIO — STATIC QC
================================================================================

Run this after every change:

    python3 tools/validate.py

It checks the generated site for the things that are easy to break and hard to
notice: broken links, missing images, malformed HTML, heading order, and the
image dimensions that keep the layout from jumping as it loads.

Exit code 0 = everything passed. Non-zero = something needs attention.
================================================================================
"""

import os, re, glob, sys, json, html.parser, subprocess, shutil

HERE    = os.path.dirname(os.path.abspath(__file__))
ROOT    = os.path.normpath(os.path.join(HERE, ".."))
WEB     = os.path.join(ROOT, "website")
CONTENT = os.path.join(WEB, "content")
PRESETS = os.path.join(ROOT, "image-prep", "presets.json")


class P(html.parser.HTMLParser):
    VOID = {'img', 'br', 'hr', 'meta', 'link', 'input', 'source',
            'area', 'base', 'col', 'embed', 'param', 'track', 'wbr'}

    def __init__(self):
        super().__init__()
        self.stack, self.imgs, self.h, self.links, self.err = [], [], [], [], []

    def handle_starttag(self, t, a):
        d = dict(a)
        if t == 'img':
            self.imgs.append(d)
        if re.fullmatch(r'h[1-6]', t):
            self.h.append(int(t[1]))
        if t == 'a' and 'href' in d:
            self.links.append(d['href'])
        if t not in self.VOID:
            self.stack.append(t)

    def handle_endtag(self, t):
        if t in self.VOID:
            return
        if not self.stack:
            self.err.append(f"stray </{t}>")
            return
        if self.stack[-1] != t:
            if t in self.stack:
                while self.stack and self.stack[-1] != t:
                    self.err.append(f"unclosed <{self.stack.pop()}>")
                self.stack.pop()
            else:
                self.err.append(f"stray </{t}>")
        else:
            self.stack.pop()


def check_pages():
    os.chdir(WEB)
    fails = []
    pages = sorted(glob.glob("*.html"))
    print(f"\n{'PAGE':<40} {'h1':>3} {'jump':>7} {'img':>4} "
          f"{'noalt':>6} {'no-wh':>6} {'dead':>5} {'miss':>5} {'nest':>5}")
    print("-" * 96)

    for f in pages:
        src = open(f, encoding='utf-8').read()

        # Redirect stubs for retired projects are intentionally minimal
        if 'http-equiv="refresh"' in src:
            print(f"{f:<40} {'-':>3} {'-':>7} {'-':>4} {'-':>6} {'-':>6} "
                  f"{'-':>5} {'-':>5} {'-':>5}   (redirect)")
            continue

        p = P()
        p.feed(src)

        n1 = p.h.count(1)
        jump, prev = None, 0
        for lv in p.h:
            if prev and lv > prev + 1:
                jump = f"h{prev}>h{lv}"
                break
            prev = lv

        noalt = [i for i in p.imgs if 'alt' not in i]
        nowh  = [i for i in p.imgs if not (i.get('width') and i.get('height'))]
        miss  = [i['src'] for i in p.imgs
                 if i.get('src') and not i['src'].startswith(('http', 'data:'))
                 and not os.path.exists(i['src'])]
        dead  = [h for h in p.links
                 if not h.startswith(('http', 'mailto:', 'tel:', '#')) and h
                 and not os.path.exists(h.split('?')[0].split('#')[0])]

        ok = n1 == 1 and not (jump or noalt or nowh or dead or miss or p.err or p.stack)
        print(f"{f:<40} {n1:>3} {jump or '-':>7} {len(p.imgs):>4} "
              f"{len(noalt):>6} {len(nowh):>6} {len(dead):>5} {len(miss):>5} {len(p.err):>5}"
              + ("" if ok else "   <-- FAIL"))
        for m in miss[:3]:
            print(f"       missing image: {m}")
        for d_ in dead[:3]:
            print(f"       dead link: {d_}")
        if not ok:
            fails.append(f)
    return fails, pages


def check_content():
    """The JSON must parse, and every project must have its images."""
    problems = []
    print("\nCONTENT")
    for name in ("site.json", "about.json", "news.json"):
        p = os.path.join(CONTENT, name)
        try:
            json.load(open(p, encoding="utf-8"))
            print(f"  {name:<24} valid")
        except Exception as e:
            print(f"  {name:<24} INVALID — {e}")
            problems.append(name)

    projs = sorted(glob.glob(os.path.join(CONTENT, "projects", "*", "project.json")))
    print(f"  {len(projs)} project(s)")
    try:
        cats = {c["slug"] for c in
                json.load(open(os.path.join(CONTENT, "site.json"), encoding="utf-8"))["categories"]}
    except Exception:
        cats = set()

    for pj in projs:
        d_ = os.path.dirname(pj)
        slug = os.path.basename(d_)
        try:
            j = json.load(open(pj, encoding="utf-8"))
        except Exception as e:
            print(f"    {slug}: INVALID JSON — {e}")
            problems.append(slug)
            continue

        issues = []
        for k in ("cover", "hero"):
            if not os.path.exists(os.path.join(d_, j.get(k, k + ".jpg"))):
                issues.append(f"no {k}")
        for g in j.get("gallery", []):
            if not os.path.exists(os.path.join(d_, g["file"])):
                issues.append(f"missing {g['file']}")
        if cats and j.get("category") not in cats:
            issues.append(f"category '{j.get('category')}' is not in site.json")
        if not j.get("intro"):
            issues.append("no intro text")
        if issues:
            print(f"    {slug}: {', '.join(issues[:4])}")
            problems.append(slug)
    return problems


def check_dims():
    """presets.json and build.py must agree, or images cause layout shift."""
    print("\nIMAGE DIMENSIONS")
    src = open(os.path.join(HERE, "build.py"), encoding="utf-8").read()
    block = re.search(r'DIMS\s*=\s*\{(.*?)\n\}', src, re.S)
    if not block:
        print("  could not find the DIMS table in build.py")
        return ["DIMS"]
    dims = {m[0]: (int(m[1]), int(m[2]))
            for m in re.findall(r'"([\w-]+)":\s*\(\s*(\d+),\s*(\d+)\s*\)', block.group(1))}
    presets = json.load(open(PRESETS, encoding="utf-8"))["presets"]
    bad = []
    for name, p in presets.items():
        want, got = (p["width"], p["height"]), dims.get(name)
        if got != want:
            print(f"  MISMATCH {name}: presets.json {want} vs build.py {got}")
            bad.append(name)
    if not bad:
        print(f"  {len(presets)} presets match build.py — OK")
    return bad


def check_assets():
    print("\nASSETS")
    css_files = glob.glob(os.path.join(WEB, "assets/css/*.css"))
    css = "".join(open(x, encoding='utf-8').read() for x in css_files)
    defined = set(re.findall(r'^\s*(--[\w-]+)\s*:', css, re.M))
    used = set(re.findall(r'var\((--[\w-]+)', css))
    undef = (used - defined) - {'--i'}          # --i is set inline by JS
    print(f"  CSS vars: {len(defined)} defined, {len(used)} used, "
          f"undefined: {undef or 'none'}")

    bad = list(undef)
    for path in css_files:
        stripped = re.sub(r'/\*.*?\*/', '', open(path, encoding='utf-8').read(), flags=re.S)
        if stripped.count('{') != stripped.count('}'):
            print(f"  BRACE MISMATCH in {os.path.basename(path)}")
            bad.append(path)

    fonts = glob.glob(os.path.join(WEB, "assets/fonts/*.woff2"))
    print(f"  Fonts: {len(fonts)} woff2 file(s)"
          + ("  (none yet — falling back to system fonts)" if not fonts else ""))

    js = os.path.join(WEB, "assets/js/site.js")
    if shutil.which("node"):
        r = subprocess.run(["node", "--check", js], capture_output=True, text=True)
        print("  site.js:", "syntax OK" if r.returncode == 0 else "SYNTAX ERROR\n" + r.stderr)
        if r.returncode != 0:
            bad.append("site.js")
    else:
        print("  site.js: skipped (node not installed)")
    return bad


def main():
    print("=" * 96)
    print("  SAMPLE PORTFOLIO — VALIDATION")
    print("=" * 96)

    content_problems = check_content()
    dim_problems     = check_dims()
    page_fails, pages = check_pages()
    asset_problems   = check_assets()

    projects = len(glob.glob(os.path.join(CONTENT, "projects", "*", "project.json")))
    size = sum(os.path.getsize(f) for f in
               glob.glob(os.path.join(WEB, "**", "*"), recursive=True) if os.path.isfile(f))
    print(f"\nSITE: {len(pages)} pages, {projects} projects, {size/1024/1024:.1f} MB "
          f"(this is what uploads to Hostinger)")

    fails = page_fails + content_problems + dim_problems + asset_problems
    print("\n" + "=" * 96)
    if fails:
        print("  RESULT: PROBLEMS FOUND ->", ", ".join(str(x) for x in dict.fromkeys(fails)))
    else:
        print("  RESULT: ALL PASS")
    print("=" * 96 + "\n")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

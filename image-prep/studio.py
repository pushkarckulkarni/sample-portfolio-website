#!/usr/bin/env python3
"""
================================================================================
IMAGE STUDIO — a small control panel for the bulk image processor
================================================================================

WHY THIS EXISTS
    process.py does the work perfectly well from the terminal. This adds a
    browser window on top of it so you can *see* what is about to happen:
    which folders have photos waiting, which preset each one will get, how big
    the files are now, and what they became afterwards.

    It is not a web app. It runs entirely on your own machine, talks to nothing,
    and stops the moment you close the terminal.

RUN IT
    python3 image-prep/studio.py

    Then open http://localhost:8765 — it will try to open by itself.

REQUIREMENTS
    pip3 install --upgrade Pillow          (same as process.py — nothing else)
================================================================================
"""

import os, sys, json, http.server, socketserver, urllib.parse, threading, webbrowser, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    import process as P
except Exception as e:
    sys.exit(f"ERROR: could not load process.py — {e}")

PORT = int(os.environ.get("STUDIO_PORT", "8765"))
UI   = os.path.join(HERE, "ui")


def human(kb):
    return f"{kb/1024:.1f} MB" if kb >= 1024 else f"{kb} KB"


def build_scan():
    """Group the pending work by folder so the UI can show a tree."""
    cfg  = P.load_presets()
    jobs = P.scan(cfg)
    tree, unrouted = {}, []

    for j in jobs:
        if "skip" in j:
            unrouted.append({"rel": j["rel"], "why": j["skip"]})
            continue
        folder = os.path.dirname(j["rel"]) or "(root)"
        node = tree.setdefault(folder, {
            "folder": folder, "preset": j["preset"]["name"],
            "presetLabel": j["preset"]["label"],
            "target": f'{j["preset"]["width"]}×{j["preset"]["height"]}',
            "ratio": j["preset"]["ratio"], "maxKB": j["preset"]["maxKB"],
            "anchor": j["preset"].get("anchor", "smart"),
            "out": j["out"], "files": [],
        })
        try:
            kb = round(os.path.getsize(j["path"]) / 1024)
        except OSError:
            kb = 0
        node["files"].append({"name": os.path.basename(j["rel"]),
                              "rel": j["rel"], "kb": kb, "to": j["name"]})

    out = sorted(tree.values(), key=lambda n: n["folder"])
    for n in out:
        n["count"] = len(n["files"])
        n["totalKB"] = sum(f["kb"] for f in n["files"])
        n["totalHuman"] = human(n["totalKB"])

    # What is already live on the site, so you can see coverage at a glance
    live = {}
    for slot in ("home/hero", "home/hero-mobile", "about/principals", "about/team", "news"):
        d = os.path.join(P.CONTENT, slot)
        live[slot] = len([f for f in os.listdir(d) if f.lower().endswith(".jpg")]) if os.path.isdir(d) else 0
    projdir = os.path.join(P.CONTENT, "projects")
    projects = []
    if os.path.isdir(projdir):
        for slug in sorted(os.listdir(projdir)):
            pd = os.path.join(projdir, slug)
            if not os.path.isdir(pd):
                continue
            g = os.path.join(pd, "gallery")
            projects.append({
                "slug": slug,
                "cover": os.path.exists(os.path.join(pd, "cover.jpg")),
                "hero":  os.path.exists(os.path.join(pd, "hero.jpg")),
                "gallery": len([f for f in os.listdir(g) if f.lower().endswith(".jpg")]) if os.path.isdir(g) else 0,
            })

    return {"tree": out, "unrouted": unrouted, "live": live, "projects": projects,
            "presets": cfg["presets"], "inbox": P.INBOX, "content": P.CONTENT}


def run_process(payload):
    cfg     = P.load_presets()
    only    = payload.get("only") or None
    anchor  = payload.get("anchor") or None
    dry     = bool(payload.get("dryRun"))
    keep    = bool(payload.get("keep"))
    over_kb = payload.get("maxKB")

    jobs = [j for j in P.scan(cfg, only) if "skip" not in j]
    if not jobs:
        return {"ok": False, "error": "Nothing to process for that selection."}

    records, before, after = [], 0, 0
    for j in jobs:
        preset = dict(j["preset"])
        if over_kb:
            try:
                preset["maxKB"] = int(over_kb)
            except (TypeError, ValueError):
                pass
        r = P.process_one(j["path"], preset, j["out"], j["name"],
                          dry=dry, anchor_override=anchor)
        r["rel"] = j["rel"]
        records.append(r)
        before += r.get("beforeKB", 0)
        after  += r.get("afterKB", 0)

    result = {"ok": True, "records": records, "dry": dry,
              "beforeKB": before, "afterKB": after,
              "beforeHuman": human(before), "afterHuman": human(after),
              "savedPct": (100 - round(after / before * 100)) if before and after else 0}

    if not dry:
        result["jsonUpdated"] = P.sync_project_json(cfg)
        if not keep:
            import shutil, datetime
            stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            moved = 0
            for j in jobs:
                dest = os.path.join(P.ARCHIVE, stamp, j["rel"])
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                try:
                    shutil.move(j["path"], dest); moved += 1
                except Exception:
                    pass
            result["archived"] = moved
        result["log"] = os.path.basename(P.write_log(records))
    return result


def run_build():
    """Convenience: rebuild the HTML without leaving the panel."""
    import subprocess
    script = os.path.join(P.ROOT, "tools", "build.py")
    try:
        r = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=180)
        return {"ok": r.returncode == 0, "out": r.stdout + r.stderr}
    except Exception as e:
        return {"ok": False, "out": str(e)}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=UI, **kw)

    def log_message(self, *a):
        pass                                   # keep the terminal quiet

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        try:
            if path == "/api/scan":
                return self._json(build_scan())
            if path == "/api/preview":
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                rel = (q.get("rel") or [""])[0]
                full = os.path.normpath(os.path.join(P.INBOX, rel))
                if not full.startswith(P.INBOX) or not os.path.isfile(full):
                    return self._json({"error": "not found"}, 404)
                from PIL import Image, ImageOps
                import io
                im = ImageOps.exif_transpose(Image.open(full))
                if im.mode != "RGB":
                    im = im.convert("RGB")
                im.thumbnail((420, 420))
                buf = io.BytesIO(); im.save(buf, "JPEG", quality=70)
                data = buf.getvalue()
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                return self.wfile.write(data)
        except Exception:
            return self._json({"error": traceback.format_exc()}, 500)
        return super().do_GET()

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        n = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            payload = {}
        try:
            if path == "/api/process":
                return self._json(run_process(payload))
            if path == "/api/build":
                return self._json(run_build())
        except Exception:
            return self._json({"ok": False, "error": traceback.format_exc()}, 500)
        return self._json({"error": "unknown endpoint"}, 404)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    os.makedirs(UI, exist_ok=True)
    url = f"http://localhost:{PORT}"
    print("\n" + "=" * 62)
    print("  IMAGE STUDIO")
    print("=" * 62)
    print(f"  Open:   {url}")
    print(f"  Inbox:  {P.INBOX}")
    print(f"  Output: {P.CONTENT}")
    print("\n  Press Ctrl+C to stop.")
    print("=" * 62 + "\n")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        with Server(("127.0.0.1", PORT), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.\n")
    except OSError as e:
        sys.exit(f"\nCould not start on port {PORT} — {e}\n"
                 f"Something else may be using it. Try:  STUDIO_PORT=8788 python3 image-prep/studio.py\n")

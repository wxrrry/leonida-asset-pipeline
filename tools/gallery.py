"""Standalone local 3D Web Studio & Texture Gallery server.

Launches a lightweight local HTTP server and opens a modern WebGL/glTF
3D asset inspector in the browser.

Usage:
    python -I tools/gallery.py [--port 8080] [--models-dir <path>] [--textures-dir <path>]
"""
from __future__ import annotations

import argparse
import http.server
import json
import mimetypes
import os
import socketserver
import sys
import urllib.parse
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import dds_png
except ImportError:
    dds_png = None


def categorize_model(name: str) -> str:
    n = name.lower()
    if any(k in n for k in ("ped", "female", "male", "head", "body", "lucia", "jacket", "hair", "face")):
        return "Character"
    elif any(k in n for k in ("veh", "car", "truck", "bike", "wheel", "heli", "boat", "chassis")):
        return "Vehicle"
    elif any(k in n for k in ("build", "structure", "house", "bridge", "farlod", "station", "shop", "wall")):
        return "Architecture"
    elif any(k in n for k in ("weapon", "gun", "pistol", "rifle", "knife", "ammo")):
        return "Weapon"
    elif any(k in n for k in ("tree", "grass", "plant", "bush", "flower")):
        return "Nature"
    return "Prop"


class StudioHandler(http.server.BaseHTTPRequestHandler):
    models_dir: str = ""
    textures_dir: str = ""
    viewer_dir: str = ""

    def log_message(self, format: str, *args: object) -> None:
        pass  # Quiet logging

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)

        if path in ("/", "/index.html"):
            index_path = os.path.join(self.viewer_dir, "index.html")
            if os.path.isfile(index_path):
                self._send_file(index_path, "text/html; charset=utf-8")
            else:
                self.send_error(404, "index.html not found")
            return

        if path.startswith("/vendor/"):
            rel = path[len("/vendor/"):]
            vpath = os.path.join(self.viewer_dir, "vendor", rel)
            if os.path.isfile(vpath):
                mime = mimetypes.guess_type(vpath)[0] or "application/javascript"
                self._send_file(vpath, mime)
            else:
                self.send_error(404, "Vendor file not found")
            return

        if path == "/api/models":
            self._serve_models_json()
            return

        if path == "/api/textures":
            self._serve_textures_json()
            return

        if path.startswith("/models/"):
            rel = path[len("/models/"):]
            mpath = os.path.join(self.models_dir, rel)
            if os.path.isfile(mpath):
                self._send_file(mpath, "model/gltf-binary")
            else:
                self.send_error(404, "Model not found")
            return

        if path.startswith("/textures/"):
            rel = path[len("/textures/"):]
            tpath = os.path.join(self.textures_dir, rel)
            if not os.path.isfile(tpath) and rel.lower().endswith(".png"):
                # Try matching .dds file if png requested
                stem = os.path.splitext(rel)[0]
                dds_cand = os.path.join(self.textures_dir, stem + ".dds")
                if os.path.isfile(dds_cand) and dds_png:
                    try:
                        png_bytes = dds_png.dds_file_to_png_bytes(dds_cand, max_size=1024)
                        self.send_response(200)
                        self.send_header("Content-Type", "image/png")
                        self.send_header("Content-Length", str(len(png_bytes)))
                        self.send_header("Cache-Control", "max-age=86400")
                        self.end_headers()
                        self.wfile.write(png_bytes)
                        return
                    except Exception:
                        pass
            if os.path.isfile(tpath):
                mime = mimetypes.guess_type(tpath)[0] or "application/octet-stream"
                self._send_file(tpath, mime)
            else:
                self.send_error(404, "Texture not found")
            return

        self.send_error(404, "Not Found")

    def _send_file(self, file_path: str, content_type: str) -> None:
        try:
            size = os.path.getsize(file_path)
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(size))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            with open(file_path, "rb") as f:
                while chunk := f.read(65536):
                    self.wfile.write(chunk)
        except Exception as exc:
            self.send_error(500, str(exc))

    def _serve_models_json(self) -> None:
        items = []
        if os.path.isdir(self.models_dir):
            for entry in os.scandir(self.models_dir):
                if entry.is_file() and entry.name.lower().endswith((".glb", ".gltf")):
                    items.append({
                        "name": entry.name,
                        "size": entry.stat().st_size,
                        "category": categorize_model(entry.name),
                        "url": f"/models/{urllib.parse.quote(entry.name)}",
                    })
        items.sort(key=lambda x: (x["category"], x["name"]))
        payload = json.dumps({"count": len(items), "models": items}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _serve_textures_json(self) -> None:
        items = []
        if os.path.isdir(self.textures_dir):
            for entry in os.scandir(self.textures_dir):
                if entry.is_file() and entry.name.lower().endswith((".dds", ".png")):
                    lower = entry.name.lower()
                    fmt = "DDS (DirectDraw Surface)" if lower.endswith(".dds") else "PNG Image"
                    preview_name = os.path.splitext(entry.name)[0] + ".png" if lower.endswith(".dds") else entry.name
                    items.append({
                        "name": entry.name,
                        "size": entry.stat().st_size,
                        "format": fmt,
                        "url": f"/textures/{urllib.parse.quote(entry.name)}",
                        "preview": f"/textures/{urllib.parse.quote(preview_name)}",
                    })
        items.sort(key=lambda x: x["name"])
        payload = json.dumps({"count": len(items), "textures": items}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def start_server(
    port: int = 8080,
    models_dir: str | None = None,
    textures_dir: str | None = None,
    open_browser: bool = True,
) -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    viewer_dir = os.path.join(root, "viewer")

    # Auto-locate default directories
    if not models_dir or not os.path.isdir(models_dir):
        cand1 = os.path.join(root, "..", "batch_converted_glb")
        cand2 = os.path.join(root, "models")
        models_dir = cand1 if os.path.isdir(cand1) else cand2

    if not textures_dir or not os.path.isdir(textures_dir):
        cand1 = os.path.join(root, "..", "clean_vehicles", "ttdb_vehicles")
        cand2 = os.path.join(root, "textures")
        textures_dir = cand1 if os.path.isdir(cand1) else cand2

    StudioHandler.models_dir = os.path.abspath(models_dir) if models_dir else ""
    StudioHandler.textures_dir = os.path.abspath(textures_dir) if textures_dir else ""
    StudioHandler.viewer_dir = viewer_dir

    addr = ("127.0.0.1", port)
    class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
        daemon_threads = True

    try:
        httpd = ThreadingServer(addr, StudioHandler)
    except OSError:
        addr = ("127.0.0.1", port + 1)
        httpd = ThreadingServer(addr, StudioHandler)

    url = f"http://localhost:{addr[1]}"
    print(f"=== Leonida 3D Asset Studio ===")
    print(f"Server running at: {url}")
    print(f"Models directory:   {StudioHandler.models_dir}")
    print(f"Textures directory: {StudioHandler.textures_dir}")
    print(f"Press Ctrl+C to stop.")

    if open_browser:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Leonida 3D Asset Studio local web gallery.")
    parser.add_argument("--port", type=int, default=8080, help="HTTP port (default 8080)")
    parser.add_argument("--models-dir", type=str, default=None, help="Directory containing .glb models")
    parser.add_argument("--textures-dir", type=str, default=None, help="Directory containing textures")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")

    args = parser.parse_args(argv)
    start_server(
        port=args.port,
        models_dir=args.models_dir,
        textures_dir=args.textures_dir,
        open_browser=not args.no_browser,
    )
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="replace")
    sys.exit(main())

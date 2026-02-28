"""
Flask web interface for ORT Henry Ronson School Bell Generator.

Binds to 0.0.0.0 so it is reachable from any device on the local network
(Mac, iPhone, etc.) at http://<server-ip>:5000

Usage:
    python app.py
"""

import os
import re
import threading
from flask import Flask, render_template, send_from_directory, jsonify, request

from pipeline import run_pipeline

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder name pattern: DD-MM-YY-V  (e.g. 04-03-25-1)
_FOLDER_RE = re.compile(r"^\d{2}-\d{2}-\d{2}-\d+$")

# Generation state (protected by a simple lock)
_lock = threading.Lock()
_gen = {"running": False, "log": [], "error": None}


def _scan_songs():
    """Return a list of generated songs sorted newest first."""
    songs = []
    for name in sorted(os.listdir(BASE_DIR), reverse=True):
        if not _FOLDER_RE.match(name):
            continue
        folder_path = os.path.join(BASE_DIR, name)
        if not os.path.isdir(folder_path):
            continue
        song = {
            "name": name,
            "audio": f"/media/{name}/song.mp3" if os.path.exists(os.path.join(folder_path, "song.mp3")) else None,
            "image": f"/media/{name}/cover.jpeg" if os.path.exists(os.path.join(folder_path, "cover.jpeg")) else None,
        }
        songs.append(song)
    return songs


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", songs=_scan_songs())


@app.route("/media/<folder>/<filename>")
def media(folder, filename):
    """Serve mp3 / jpeg files from date-stamped output folders."""
    if not _FOLDER_RE.match(folder):
        return "Not found", 404
    safe_name = os.path.basename(filename)
    return send_from_directory(os.path.join(BASE_DIR, folder), safe_name)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    with _lock:
        if _gen["running"]:
            return jsonify({"error": "Generation already running"}), 409
        _gen["running"] = True
        _gen["log"] = []
        _gen["error"] = None

    def _log(msg):
        with _lock:
            _gen["log"].append(str(msg))

    def _worker():
        try:
            run_pipeline(log=_log)
        except Exception as exc:
            with _lock:
                _gen["error"] = str(exc)
                _gen["log"].append(f"Error: {exc}")
        finally:
            with _lock:
                _gen["running"] = False

    threading.Thread(target=_worker, daemon=True).start()
    return jsonify({"message": "Generation started"})


@app.route("/api/status")
def api_status():
    with _lock:
        return jsonify(dict(_gen))


@app.route("/api/songs")
def api_songs():
    return jsonify(_scan_songs())


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import socket
    # Try to find the local LAN IP to print a helpful URL
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"

    print(f"\n{'═'*55}")
    print(f"  ORT Henry Ronson — School Bell Web Interface")
    print(f"{'═'*55}")
    print(f"  Local:    http://127.0.0.1:5000")
    print(f"  Network:  http://{local_ip}:5000   ← open on Mac / iPhone")
    print(f"{'═'*55}\n")

    app.run(host="0.0.0.0", port=5000, debug=False)

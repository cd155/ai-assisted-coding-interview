from flask import Flask, request, jsonify, send_file
import sqlite3
import os
import random
import string
import logging
from datetime import datetime, timedelta
from pathlib import Path

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DB_PATH", "fileshare.db")
UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shares (
            token TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            stored_path TEXT NOT NULL,
            content_type TEXT,
            size_bytes INTEGER,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT,
            max_downloads INTEGER,
            download_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def generate_token():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "file required"}), 400

    file = request.files["file"]
    filename = file.filename

    expires_in_hours = int(request.form.get("expires_in_hours", 24))
    max_downloads = int(request.form.get("max_downloads", 10))

    logger.info(f"Uploading {filename}")

    token = generate_token()

    stored_path = UPLOAD_DIR / filename
    file.save(str(stored_path))
    size = stored_path.stat().st_size

    expires_at = (datetime.utcnow() + timedelta(hours=expires_in_hours)).isoformat()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO shares (token, filename, stored_path, content_type, size_bytes, expires_at, max_downloads)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (token, filename, str(stored_path), file.content_type, size, expires_at, max_downloads))
    conn.commit()
    conn.close()

    return jsonify({
        "token": token,
        "share_url": request.host_url.rstrip("/") + "/" + token,
        "expires_at": expires_at,
        "max_downloads": max_downloads
    }), 201


@app.route("/<token>", methods=["GET"])
def download(token):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shares WHERE token = ?", (token,))
    share = cursor.fetchone()

    if not share:
        conn.close()
        return jsonify({"error": "not found"}), 404

    if share["download_count"] >= share["max_downloads"]:
        conn.close()
        return jsonify({"error": "download limit reached"}), 410

    new_count = share["download_count"] + 1
    cursor.execute("UPDATE shares SET download_count = ? WHERE token = ?", (new_count, token))
    conn.commit()
    conn.close()

    return send_file(
        share["stored_path"],
        download_name=share["filename"],
        as_attachment=True
    )


@app.route("/info/<token>", methods=["GET"])
def info(token):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT token, filename, content_type, size_bytes, uploaded_at,
               expires_at, max_downloads, download_count
        FROM shares WHERE token = ?
    """, (token,))
    share = cursor.fetchone()
    conn.close()

    if not share:
        return jsonify({"error": "not found"}), 404

    return jsonify(dict(share))


@app.route("/<token>", methods=["DELETE"])
def delete(token):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT stored_path FROM shares WHERE token = ?", (token,))
    share = cursor.fetchone()

    if not share:
        conn.close()
        return jsonify({"error": "not found"}), 404

    try:
        Path(share["stored_path"]).unlink()
    except FileNotFoundError:
        pass

    cursor.execute("DELETE FROM shares WHERE token = ?", (token,))
    conn.commit()
    conn.close()

    return jsonify({"status": "deleted"})


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "8080"))
    app.run(debug=True, host="127.0.0.1", port=port)

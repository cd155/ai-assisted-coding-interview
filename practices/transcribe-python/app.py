from flask import Flask, request, jsonify
import sqlite3
import secrets
import logging
import os
import threading
import time
import requests
from transcription_service import transcribe_audio

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DB_PATH", "transcribe.db")
WORKER_ID = secrets.token_hex(4)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audio_url TEXT NOT NULL,
            language TEXT,
            status TEXT DEFAULT 'queued',
            result TEXT,
            error TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            claimed_at TEXT,
            claimed_by TEXT,
            completed_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/jobs", methods=["POST"])
def create_job():
    data = request.get_json()
    audio_url = data.get("audio_url")
    language = data.get("language", "en")

    if not audio_url:
        return jsonify({"error": "audio_url required"}), 400

    logger.info(f"New job: url={audio_url}, language={language}")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO jobs (audio_url, language) VALUES (?, ?)",
        (audio_url, language)
    )
    job_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({"id": job_id, "status": "queued"}), 201


@app.route("/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    conn.close()

    if not job:
        return jsonify({"error": "not found"}), 404

    return jsonify(dict(job))


@app.route("/jobs", methods=["GET"])
def list_jobs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, status, created_at FROM jobs ORDER BY created_at DESC LIMIT 100")
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(jobs)


def process_one_job():
    """Process a single queued job. Returns job_id processed, or None if no work."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs WHERE status = 'queued' ORDER BY id LIMIT 1")
    job = cursor.fetchone()

    if not job:
        conn.close()
        return None

    cursor.execute("""
        UPDATE jobs SET status = 'running',
                        claimed_at = CURRENT_TIMESTAMP,
                        claimed_by = ?
        WHERE id = ?
    """, (WORKER_ID, job["id"]))
    conn.commit()

    try:
        response = requests.get(job["audio_url"], timeout=30)
        audio_data = response.content

        result = transcribe_audio(audio_data, job["language"])

        cursor.execute("""
            UPDATE jobs SET status = 'done',
                            result = ?,
                            completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (result, job["id"]))
        conn.commit()
    except Exception as e:
        logger.error(f"Transcription failed for job {job['id']}: {e}")

    conn.close()
    return job["id"]


def worker_loop():
    while True:
        try:
            if process_one_job() is None:
                time.sleep(1)
        except Exception as e:
            logger.error(f"Worker loop error: {e}")
            time.sleep(1)


_worker_thread = None


def start_worker():
    global _worker_thread
    if _worker_thread is None or not _worker_thread.is_alive():
        _worker_thread = threading.Thread(target=worker_loop, daemon=True)
        _worker_thread.start()


if __name__ == "__main__":
    init_db()
    start_worker()
    port = int(os.environ.get("PORT", "8080"))
    app.run(debug=True, host="127.0.0.1", port=port)

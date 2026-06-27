from flask import Flask, request, jsonify, session, redirect
import sqlite3
import secrets
import logging
import os
from email_service import send_magic_link

app = Flask(__name__)
app.secret_key = "linklock-default-secret"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DB_PATH", "linklock.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS magic_tokens (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            redirect_to TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            used INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/auth/request", methods=["POST"])
def request_link():
    data = request.get_json()
    email = data.get("email")
    redirect_to = data.get("redirect_to", "/me")

    if not email:
        return jsonify({"error": "email required"}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (email) VALUES (?)", (email,))
        user_id = cursor.lastrowid
        conn.commit()
        new_user = True
    else:
        user_id = user["id"]
        new_user = False

    token = secrets.token_urlsafe(24)
    cursor.execute(
        "INSERT INTO magic_tokens (token, user_id, redirect_to) VALUES (?, ?, ?)",
        (token, user_id, redirect_to)
    )
    conn.commit()
    conn.close()

    logger.info(f"Sending magic link to {email}: token={token}, redirect_to={redirect_to}")

    send_magic_link(email, token, redirect_to)

    if new_user:
        return jsonify({"status": "user created, link sent"})
    return jsonify({"status": "link sent"})


@app.route("/auth/verify", methods=["GET"])
def verify():
    token = request.args.get("token")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM magic_tokens WHERE token = ?", (token,))
    record = cursor.fetchone()

    if not record:
        conn.close()
        return jsonify({"error": "invalid token"}), 401

    if record["used"]:
        conn.close()
        return jsonify({"error": "token already used"}), 401

    cursor.execute("UPDATE magic_tokens SET used = 1 WHERE token = ?", (token,))
    conn.commit()

    session["user_id"] = record["user_id"]
    redirect_to = record["redirect_to"] or "/me"

    conn.close()
    return redirect(redirect_to)


@app.route("/me")
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "not authenticated"}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "user not found"}), 404

    return jsonify(dict(user))


@app.route("/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "logged out"})


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "8080"))
    app.run(debug=True, host="127.0.0.1", port=port)

from flask import Flask, request, jsonify
import sqlite3
import logging
import os
from email_service import send_booking_confirmation

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DB_PATH", "schedulr.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT NOT NULL,
            start_at TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            booked INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_id INTEGER NOT NULL,
            guest_name TEXT NOT NULL,
            guest_email TEXT NOT NULL,
            booked_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/slots", methods=["POST"])
def create_slot():
    data = request.get_json()
    host = data.get("host")
    start_at = data.get("start_at")
    duration = data.get("duration_minutes", 30)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO slots (host, start_at, duration_minutes) VALUES (?, ?, ?)",
        (host, start_at, duration)
    )
    slot_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"id": slot_id}), 201


@app.route("/availability/<host>", methods=["GET"])
def availability(host):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM slots WHERE host = ? AND booked = 0 ORDER BY start_at",
        (host,)
    )
    slots = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(slots)


@app.route("/book", methods=["POST"])
def book():
    data = request.get_json()
    slot_id = data.get("slot_id")
    guest_name = data.get("guest_name")
    guest_email = data.get("guest_email")

    logger.info(f"Booking slot {slot_id} for {guest_name} <{guest_email}>")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM slots WHERE id = ?", (slot_id,))
    slot = cursor.fetchone()

    if not slot:
        conn.close()
        return jsonify({"error": "slot not found"}), 404

    if slot["booked"]:
        conn.close()
        return jsonify({"error": "slot already booked"}), 409

    cursor.execute(
        "INSERT INTO bookings (slot_id, guest_name, guest_email) VALUES (?, ?, ?)",
        (slot_id, guest_name, guest_email)
    )
    cursor.execute("UPDATE slots SET booked = 1 WHERE id = ?", (slot_id,))
    conn.commit()
    booking_id = cursor.lastrowid

    try:
        send_booking_confirmation(guest_email, slot["host"], slot["start_at"])
    except Exception as e:
        logger.error(f"Email failed: {e}")

    conn.close()
    return jsonify({"booking_id": booking_id}), 201


@app.route("/bookings/<host>", methods=["GET"])
def list_bookings(host):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT bookings.*, slots.start_at, slots.duration_minutes
        FROM bookings JOIN slots ON bookings.slot_id = slots.id
        WHERE slots.host = ?
        ORDER BY slots.start_at
    """, (host,))
    bookings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(bookings)


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "8080"))
    app.run(debug=True, host="127.0.0.1", port=port)

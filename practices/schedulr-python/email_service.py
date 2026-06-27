import time
import random
import os

EMAIL_LATENCY_MS = int(os.environ.get("EMAIL_LATENCY_MS", "300"))
EMAIL_FAILURE_RATE = float(os.environ.get("EMAIL_FAILURE_RATE", "0.05"))


def send_booking_confirmation(to_email, host, start_at):
    """Send a booking confirmation email. Slow and occasionally fails."""
    if not to_email:
        raise ValueError("email required")

    time.sleep(EMAIL_LATENCY_MS / 1000)

    if random.random() < EMAIL_FAILURE_RATE:
        raise Exception("email service unavailable")

    return {"sent": True, "to": to_email}

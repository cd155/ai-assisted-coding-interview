import time
import random
import os

EMAIL_LATENCY_MS = int(os.environ.get("EMAIL_LATENCY_MS", "300"))
EMAIL_FAILURE_RATE = float(os.environ.get("EMAIL_FAILURE_RATE", "0.05"))
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080")


def send_magic_link(to_email, token, redirect_to):
    """Send a magic-link email. Slow and occasionally fails."""
    if not to_email:
        raise ValueError("email required")

    time.sleep(EMAIL_LATENCY_MS / 1000)

    if random.random() < EMAIL_FAILURE_RATE:
        raise Exception("email service unavailable")

    link = f"{BASE_URL}/auth/verify?token={token}"
    return {"sent": True, "to": to_email, "link": link}

import time
import random
import os

TRANSCRIPTION_LATENCY_MS = int(os.environ.get("TRANSCRIPTION_LATENCY_MS", "500"))
TRANSCRIPTION_FAILURE_RATE = float(os.environ.get("TRANSCRIPTION_FAILURE_RATE", "0.10"))


def transcribe_audio(audio_data, language="en"):
    """Mock transcription. Slow and occasionally fails."""
    time.sleep(TRANSCRIPTION_LATENCY_MS / 1000)

    if random.random() < TRANSCRIPTION_FAILURE_RATE:
        raise Exception("transcription model unavailable")

    return f"[{language}] mock transcription of {len(audio_data)} bytes"

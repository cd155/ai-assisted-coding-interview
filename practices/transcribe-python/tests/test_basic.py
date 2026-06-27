import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    os.environ["DB_PATH"] = db_path
    os.environ["TRANSCRIPTION_LATENCY_MS"] = "10"
    os.environ["TRANSCRIPTION_FAILURE_RATE"] = "0"

    import importlib
    import app as app_module
    importlib.reload(app_module)
    app_module.init_db()

    with app_module.app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)


def test_create_job(client):
    r = client.post("/jobs", json={
        "audio_url": "https://example.com/audio.mp3",
        "language": "en"
    })
    assert r.status_code == 201
    assert r.get_json()["status"] == "queued"


def test_get_job(client):
    r = client.post("/jobs", json={"audio_url": "https://example.com/audio.mp3"})
    job_id = r.get_json()["id"]

    r = client.get(f"/jobs/{job_id}")
    assert r.status_code == 200
    assert r.get_json()["status"] == "queued"


def test_process_completes_job(client):
    r = client.post("/jobs", json={"audio_url": "https://example.com/audio.mp3"})
    job_id = r.get_json()["id"]

    import app as app_module
    fake_response = MagicMock()
    fake_response.content = b"fake audio data"
    with patch("app.requests.get", return_value=fake_response):
        app_module.process_one_job()

    r = client.get(f"/jobs/{job_id}")
    assert r.get_json()["status"] == "done"


def test_list_jobs(client):
    client.post("/jobs", json={"audio_url": "https://example.com/a.mp3"})
    client.post("/jobs", json={"audio_url": "https://example.com/b.mp3"})

    r = client.get("/jobs")
    assert len(r.get_json()) == 2


def test_invalid_job_returns_404(client):
    r = client.get("/jobs/9999")
    assert r.status_code == 404

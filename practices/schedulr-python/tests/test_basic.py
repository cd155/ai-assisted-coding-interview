import pytest
import os
import tempfile


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    os.environ["DB_PATH"] = db_path
    os.environ["EMAIL_LATENCY_MS"] = "10"
    os.environ["EMAIL_FAILURE_RATE"] = "0"

    import importlib
    import app as app_module
    importlib.reload(app_module)

    app_module.init_db()
    with app_module.app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)


def test_create_slot(client):
    r = client.post("/slots", json={
        "host": "alice",
        "start_at": "2026-06-01T14:00:00",
        "duration_minutes": 30
    })
    assert r.status_code == 201
    assert "id" in r.get_json()


def test_lists_availability(client):
    client.post("/slots", json={"host": "alice", "start_at": "2026-06-01T14:00:00"})
    client.post("/slots", json={"host": "alice", "start_at": "2026-06-01T15:00:00"})

    r = client.get("/availability/alice")
    assert len(r.get_json()) == 2


def test_book_slot(client):
    r = client.post("/slots", json={"host": "alice", "start_at": "2026-06-01T14:00:00"})
    slot_id = r.get_json()["id"]

    r = client.post("/book", json={
        "slot_id": slot_id,
        "guest_name": "Bob",
        "guest_email": "bob@example.com"
    })
    assert r.status_code == 201


def test_double_book_returns_409(client):
    r = client.post("/slots", json={"host": "alice", "start_at": "2026-06-01T14:00:00"})
    slot_id = r.get_json()["id"]

    client.post("/book", json={"slot_id": slot_id, "guest_name": "Bob", "guest_email": "b@e.com"})
    r = client.post("/book", json={"slot_id": slot_id, "guest_name": "Carol", "guest_email": "c@e.com"})
    assert r.status_code == 409


def test_lists_bookings_for_host(client):
    r = client.post("/slots", json={"host": "alice", "start_at": "2026-06-01T14:00:00"})
    slot_id = r.get_json()["id"]
    client.post("/book", json={"slot_id": slot_id, "guest_name": "Bob", "guest_email": "b@e.com"})

    r = client.get("/bookings/alice")
    assert len(r.get_json()) == 1

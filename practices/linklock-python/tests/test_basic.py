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


def test_request_returns_200(client):
    r = client.post("/auth/request", json={"email": "test@example.com"})
    assert r.status_code == 200


def test_verify_logs_in_user(client):
    client.post("/auth/request", json={"email": "alice@example.com"})

    import app as app_module
    conn = app_module.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT token FROM magic_tokens LIMIT 1")
    token = cursor.fetchone()["token"]
    conn.close()

    r = client.get(f"/auth/verify?token={token}", follow_redirects=False)
    assert r.status_code in (302, 303)


def test_me_requires_auth(client):
    r = client.get("/me")
    assert r.status_code == 401


def test_me_after_verify(client):
    client.post("/auth/request", json={"email": "bob@example.com"})

    import app as app_module
    conn = app_module.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT token FROM magic_tokens LIMIT 1")
    token = cursor.fetchone()["token"]
    conn.close()

    client.get(f"/auth/verify?token={token}", follow_redirects=False)

    r = client.get("/me")
    assert r.status_code == 200
    assert r.get_json()["email"] == "bob@example.com"


def test_invalid_token_rejected(client):
    r = client.get("/auth/verify?token=not_a_real_token")
    assert r.status_code == 401


def test_logout_clears_session(client):
    client.post("/auth/request", json={"email": "carol@example.com"})

    import app as app_module
    conn = app_module.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT token FROM magic_tokens LIMIT 1")
    token = cursor.fetchone()["token"]
    conn.close()

    client.get(f"/auth/verify?token={token}", follow_redirects=False)
    client.post("/auth/logout")

    r = client.get("/me")
    assert r.status_code == 401

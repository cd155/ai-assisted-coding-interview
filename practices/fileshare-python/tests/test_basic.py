import pytest
import os
import tempfile
import io


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    upload_dir = tempfile.mkdtemp()
    os.environ["DB_PATH"] = db_path
    os.environ["UPLOAD_DIR"] = upload_dir

    import importlib
    import app as app_module
    importlib.reload(app_module)
    app_module.init_db()

    with app_module.app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)


def test_upload_returns_token(client):
    data = {"file": (io.BytesIO(b"hello world"), "hello.txt")}
    r = client.post("/upload", data=data, content_type="multipart/form-data")
    assert r.status_code == 201
    assert "token" in r.get_json()


def test_download_returns_file(client):
    data = {"file": (io.BytesIO(b"hello world"), "hello.txt")}
    r = client.post("/upload", data=data, content_type="multipart/form-data")
    token = r.get_json()["token"]

    r = client.get(f"/{token}")
    assert r.status_code == 200
    assert r.data == b"hello world"


def test_info_returns_metadata(client):
    data = {"file": (io.BytesIO(b"hello"), "hello.txt")}
    r = client.post("/upload", data=data, content_type="multipart/form-data")
    token = r.get_json()["token"]

    r = client.get(f"/info/{token}")
    assert r.get_json()["filename"] == "hello.txt"


def test_max_downloads_enforced(client):
    data = {"file": (io.BytesIO(b"data"), "test.txt"), "max_downloads": "2"}
    r = client.post("/upload", data=data, content_type="multipart/form-data")
    token = r.get_json()["token"]

    client.get(f"/{token}")
    client.get(f"/{token}")
    r = client.get(f"/{token}")
    assert r.status_code == 410


def test_delete_removes_share(client):
    data = {"file": (io.BytesIO(b"data"), "test.txt")}
    r = client.post("/upload", data=data, content_type="multipart/form-data")
    token = r.get_json()["token"]

    r = client.delete(f"/{token}")
    assert r.status_code == 200

    r = client.get(f"/info/{token}")
    assert r.status_code == 404


def test_unknown_token_returns_404(client):
    r = client.get("/notreal")
    assert r.status_code == 404

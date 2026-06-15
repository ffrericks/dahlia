def test_export_returns_a_zip(client):
    r = client.get("/api/backup/export")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"
    assert r.content[:2] == b"PK"  # zip magic bytes


def test_import_requires_the_confirm_phrase(client):
    snapshot = client.get("/api/backup/export").content
    r = client.post(
        "/api/backup/import",
        data={"confirm": "oeps"},
        files={"file": ("backup.zip", snapshot, "application/zip")},
    )
    assert r.status_code == 400


def test_import_rejects_non_zip(client):
    r = client.post(
        "/api/backup/import",
        data={"confirm": "dahlia tool"},
        files={"file": ("notes.txt", b"not a zip", "text/plain")},
    )
    assert r.status_code == 400


def test_import_rejects_zip_without_database(client):
    import io
    import zipfile

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("random.txt", "hello")
    r = client.post(
        "/api/backup/import",
        data={"confirm": "dahlia tool"},
        files={"file": ("backup.zip", buf.getvalue(), "application/zip")},
    )
    assert r.status_code == 400


def test_roundtrip_restores_previous_state(client):
    client.post("/api/varieties", json={"code": "AAA", "name": "A"})
    snapshot = client.get("/api/backup/export").content  # contains only AAA

    client.post("/api/varieties", json={"code": "BBB", "name": "B"})
    assert len(client.get("/api/varieties").json()) == 2

    r = client.post(
        "/api/backup/import",
        data={"confirm": "Dahlia Tool"},  # case-insensitive
        files={"file": ("backup.zip", snapshot, "application/zip")},
    )
    assert r.status_code == 200

    codes = [v["code"] for v in client.get("/api/varieties").json()]
    assert codes == ["AAA"]  # B is gone — restored to the snapshot

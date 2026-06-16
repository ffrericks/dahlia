def test_create_and_list(client):
    created = client.post(
        "/api/varieties", json={"code": "wit", "name": "Witte Dahlia"}
    )
    assert created.status_code == 201
    body = created.json()
    assert body["code"] == "WIT"  # normalized to uppercase
    assert body["name"] == "Witte Dahlia"

    listed = client.get("/api/varieties")
    assert listed.status_code == 200
    assert [v["code"] for v in listed.json()] == ["WIT"]


def test_invalid_code_is_rejected(client):
    too_long = client.post("/api/varieties", json={"code": "WITTE", "name": "X"})
    assert too_long.status_code == 422

    not_letters = client.post("/api/varieties", json={"code": "W1T", "name": "X"})
    assert not_letters.status_code == 422


def test_duplicate_code_conflicts(client):
    client.post("/api/varieties", json={"code": "ROO", "name": "Rode"})
    duplicate = client.post(
        "/api/varieties", json={"code": "roo", "name": "Andere rode"}
    )
    assert duplicate.status_code == 409


def test_update_keeps_code_but_changes_fields(client):
    variety_id = client.post(
        "/api/varieties", json={"code": "GEL", "name": "Gele"}
    ).json()["id"]

    updated = client.patch(
        f"/api/varieties/{variety_id}",
        json={"name": "Gele Dahlia", "description": "Mooie gele bloem"},
    )
    assert updated.status_code == 200
    body = updated.json()
    assert body["code"] == "GEL"
    assert body["name"] == "Gele Dahlia"
    assert body["description"] == "Mooie gele bloem"


def test_delete(client):
    variety_id = client.post(
        "/api/varieties", json={"code": "PAA", "name": "Paarse"}
    ).json()["id"]

    assert client.delete(f"/api/varieties/{variety_id}").status_code == 204
    assert client.get(f"/api/varieties/{variety_id}").status_code == 404


def test_get_missing_returns_404(client):
    assert client.get("/api/varieties/999").status_code == 404

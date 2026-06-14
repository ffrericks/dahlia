def _planted_plant(client, code="WIT"):
    """Create a plant and plant it into a new garden spot."""
    variety = client.post("/api/varieties", json={"code": code, "name": "Wit"}).json()
    plant = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety["id"]}
    ).json()
    client.post(
        "/api/plantings",
        json={"plant_id": plant["id"], "new_location_kind": "garden", "new_location_name": "Border"},
    )
    return plant


def test_lift_returns_plant_to_storage_and_closes_planting(client):
    plant = _planted_plant(client)
    lifted = client.post(f"/api/plants/{plant['id']}/lift", json={"lifted_on": "2026-11-15"})
    assert lifted.status_code == 200
    assert lifted.json()["state"] == "stored"

    detail = client.get(f"/api/plants/{plant['id']}").json()
    assert detail["location"] is None  # no longer standing anywhere
    assert detail["plantings"][0]["lifted_on"] == "2026-11-15"


def test_cannot_lift_a_stored_plant(client):
    variety = client.post("/api/varieties", json={"code": "WIT", "name": "Wit"}).json()
    plant = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety["id"]}
    ).json()
    assert client.post(f"/api/plants/{plant['id']}/lift", json={}).status_code == 400


def test_eye_status_can_be_set(client):
    plant = _planted_plant(client)
    client.post(f"/api/plants/{plant['id']}/lift", json={})
    updated = client.patch(
        f"/api/plants/{plant['id']}/eye-status", json={"eye_status": "blind"}
    )
    assert updated.status_code == 200
    assert updated.json()["eye_status"] == "blind"

    bad = client.patch(f"/api/plants/{plant['id']}/eye-status", json={"eye_status": "rotten"})
    assert bad.status_code == 422


def test_storage_box_code_and_disappears_when_empty(client):
    plant = _planted_plant(client)
    client.post(f"/api/plants/{plant['id']}/lift", json={})

    assigned = client.put(
        f"/api/plants/{plant['id']}/storage", json={"number": 1, "year": 2026}
    ).json()
    assert assigned["storage"]["box_code"] == "D0126"
    assert assigned["storage"]["composite"] == "WIT01000D0126"

    boxes = client.get("/api/storage-boxes").json()
    assert len(boxes) == 1
    assert boxes[0]["code"] == "D0126"

    # Removing the only tuber makes the box disappear.
    client.delete(f"/api/plants/{plant['id']}/storage")
    assert client.get("/api/storage-boxes").json() == []


def test_only_stored_plants_can_be_boxed(client):
    plant = _planted_plant(client)  # state is 'planted'
    response = client.put(f"/api/plants/{plant['id']}/storage", json={"number": 1, "year": 2026})
    assert response.status_code == 400


def test_planting_out_releases_the_box(client):
    plant = _planted_plant(client)
    client.post(f"/api/plants/{plant['id']}/lift", json={})
    client.put(f"/api/plants/{plant['id']}/storage", json={"number": 2, "year": 2026})
    assert len(client.get("/api/storage-boxes").json()) == 1

    # Replant the clump -> it leaves the box, box becomes empty and disappears.
    client.post(
        "/api/plantings",
        json={"plant_id": plant["id"], "new_location_kind": "garden"},
    )
    assert client.get("/api/storage-boxes").json() == []


def test_season_rollover_is_gated_and_resumes_survivors(client):
    planted = _planted_plant(client, "WIT")
    survivor = _planted_plant(client, "ROO")

    # Both are planted -> cannot start a new season yet.
    status = client.get("/api/season/status").json()
    assert status["can_start_new"] is False
    assert len(status["blocking"]) == 2
    assert client.post("/api/season/new").status_code == 400

    # Resolve them: lift one, mark the other as survived winter.
    client.post(f"/api/plants/{planted['id']}/lift", json={})
    client.post(f"/api/plants/{survivor['id']}/survive-winter")

    status = client.get("/api/season/status").json()
    assert status["can_start_new"] is True
    assert status["survived_count"] == 1

    result = client.post("/api/season/new")
    assert result.status_code == 200
    assert result.json()["resumed"] == 1
    # The survivor resumes as a planted plant of the new season.
    assert client.get(f"/api/plants/{survivor['id']}").json()["state"] == "planted"

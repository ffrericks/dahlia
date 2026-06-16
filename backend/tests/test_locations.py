def _make_plant(client, code="WIT"):
    variety = client.post("/api/varieties", json={"code": code, "name": "Wit"}).json()
    return client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety["id"]}
    ).json()


def test_location_codes_increment_per_kind(client):
    garden = client.post(
        "/api/locations", json={"kind": "garden", "name": "Border"}
    ).json()
    container = client.post("/api/locations", json={"kind": "container"}).json()
    garden2 = client.post(
        "/api/locations", json={"kind": "garden", "name": "Achtertuin"}
    ).json()

    assert garden["code"] == "T01"
    assert garden2["code"] == "T02"
    assert container["code"] == "B01"
    assert garden["label"] == "tuin"
    assert container["label"] == "pot"  # single/empty container is a pot


def test_plant_into_existing_location_sets_state_planted(client):
    plant = _make_plant(client)
    location = client.post(
        "/api/locations", json={"kind": "garden", "name": "Border"}
    ).json()

    planting = client.post(
        "/api/plantings",
        json={"plant_id": plant["id"], "location_id": location["id"]},
    )
    assert planting.status_code == 201
    assert planting.json()["location_code"] == "T01"

    detail = client.get(f"/api/plants/{plant['id']}").json()
    assert detail["state"] == "planted"
    assert detail["location"]["code"] == "T01"
    assert len(detail["plantings"]) == 1


def test_plant_into_new_location_inline(client):
    plant = _make_plant(client)
    planting = client.post(
        "/api/plantings",
        json={
            "plant_id": plant["id"],
            "new_location_kind": "container",
            "new_location_name": "Houten bak",
            "position": "voor",
        },
    ).json()
    assert planting["location_code"] == "B01"
    assert planting["position"] == "voor"


def test_container_with_two_plants_becomes_bak(client):
    a = _make_plant(client, "WIT")
    b = _make_plant(client, "ROO")
    location = client.post(
        "/api/locations", json={"kind": "container", "name": "Bak"}
    ).json()

    client.post(
        "/api/plantings",
        json={"plant_id": a["id"], "location_id": location["id"], "position": "voor"},
    )
    client.post(
        "/api/plantings",
        json={"plant_id": b["id"], "location_id": location["id"], "position": "achter"},
    )

    detail = client.get(f"/api/locations/{location['id']}").json()
    assert detail["label"] == "bak"
    assert detail["active_count"] == 2
    positions = sorted(p["position"] for p in detail["plants"])
    assert positions == ["achter", "voor"]


def test_cannot_plant_an_already_planted_plant(client):
    plant = _make_plant(client)
    location = client.post("/api/locations", json={"kind": "garden"}).json()
    client.post(
        "/api/plantings", json={"plant_id": plant["id"], "location_id": location["id"]}
    )

    again = client.post(
        "/api/plantings", json={"plant_id": plant["id"], "location_id": location["id"]}
    )
    assert again.status_code == 400


def test_used_location_cannot_be_deleted(client):
    plant = _make_plant(client)
    location = client.post("/api/locations", json={"kind": "garden"}).json()
    client.post(
        "/api/plantings", json={"plant_id": plant["id"], "location_id": location["id"]}
    )

    assert client.delete(f"/api/locations/{location['id']}").status_code == 409


def test_unused_location_can_be_deleted(client):
    location = client.post("/api/locations", json={"kind": "garden"}).json()
    assert client.delete(f"/api/locations/{location['id']}").status_code == 204


def test_care_tips_for_month(client):
    response = client.get("/api/care-tips", params={"month": 6})
    assert response.status_code == 200
    body = response.json()
    assert body["month"] == 6
    ids = {tip["id"] for tip in body["tips"]}
    # June: topping and slug protection apply; winter storage does not.
    assert "toppen" in ids
    assert "opslag" not in ids

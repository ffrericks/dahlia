def _variety(client, code):
    return client.post("/api/varieties", json={"code": code, "name": code}).json()


def _plant(client, variety_id):
    return client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety_id}
    ).json()


def test_provisional_unknown_plant_has_no_code(client):
    plant = client.post("/api/plants", json={"origin": "unknown", "nickname": "Links"}).json()
    assert plant["full_code"] is None
    assert plant["variety_id"] is None
    assert plant["nickname"] == "Links"
    assert plant["label"] == "Links"
    assert plant["origin"] == "unknown"


def test_rename_provisional_nickname(client):
    plant = client.post("/api/plants", json={"origin": "unknown", "nickname": "Links"}).json()
    renamed = client.patch(f"/api/plants/{plant['id']}", json={"nickname": "Rechts"})
    assert renamed.status_code == 200
    assert renamed.json()["nickname"] == "Rechts"


def test_assign_variety_gives_provisional_plant_a_number(client):
    variety = _variety(client, "WIT")
    plant = client.post("/api/plants", json={"origin": "unknown", "nickname": "Links"}).json()

    assigned = client.put(
        f"/api/plants/{plant['id']}/variety", json={"variety_id": variety["id"]}
    )
    assert assigned.status_code == 200
    body = assigned.json()
    assert body["full_code"] == "WIT01000"
    assert body["variety_code"] == "WIT"


def test_cannot_assign_variety_twice(client):
    variety = _variety(client, "WIT")
    plant = _plant(client, variety["id"])  # already has a variety
    response = client.put(f"/api/plants/{plant['id']}/variety", json={"variety_id": variety["id"]})
    assert response.status_code == 400


def test_cannot_split_a_provisional_plant(client):
    plant = client.post("/api/plants", json={"origin": "unknown", "nickname": "Links"}).json()
    response = client.post("/api/plants", json={"origin": "split", "parent_plant_id": plant["id"]})
    assert response.status_code == 400


def test_location_ranking_orders_by_score(client):
    wit = _variety(client, "WIT")
    roo = _variety(client, "ROO")
    good = _plant(client, wit["id"])
    weak = _plant(client, roo["id"])

    # Plant each into its own spot, then log very different growth.
    client.post("/api/plantings", json={"plant_id": good["id"], "new_location_kind": "garden", "new_location_name": "Zonnig"})
    client.post("/api/plantings", json={"plant_id": weak["id"], "new_location_kind": "garden", "new_location_name": "Schaduw"})
    client.post(f"/api/plants/{good['id']}/logs", json={"height_cm": 120, "flower_count": 20, "harvested_count": 15})
    client.post(f"/api/plants/{weak['id']}/logs", json={"height_cm": 30, "flower_count": 2, "harvested_count": 1})

    result = client.get("/api/insights/locations").json()
    rows = result["locations"]
    assert len(rows) == 2
    assert rows[0]["code"] == "T01"  # the sunny spot ranks first
    assert rows[0]["score"] >= rows[1]["score"]
    assert rows[0]["avg_height"] == 120


def test_weights_can_exclude_a_metric(client):
    wit = _variety(client, "WIT")
    plant = _plant(client, wit["id"])
    client.post("/api/plantings", json={"plant_id": plant["id"], "new_location_kind": "garden"})
    client.post(f"/api/plants/{plant['id']}/logs", json={"height_cm": 100})

    # Weighting only harvested (which is zero here) should not crash; score is 0.
    result = client.get("/api/insights/locations", params={"w_height": 0, "w_flowers": 0, "w_harvested": 1}).json()
    assert result["locations"][0]["score"] == 0.0


def test_plant_year_history_in_detail(client):
    wit = _variety(client, "WIT")
    plant = _plant(client, wit["id"])
    client.post("/api/plantings", json={"plant_id": plant["id"], "new_location_kind": "garden", "new_location_name": "Border"})
    client.post(f"/api/plants/{plant['id']}/logs", json={"height_cm": 80, "flower_count": 6})

    detail = client.get(f"/api/plants/{plant['id']}").json()
    assert len(detail["yearly"]) == 1
    assert detail["yearly"][0]["height_max"] == 80
    assert detail["yearly"][0]["location_code"] == "T01"

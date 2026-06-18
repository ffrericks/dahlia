def _stam(client, code="WIT"):
    v = client.post("/api/varieties", json={"code": code, "name": code}).json()
    return client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": v["id"]}
    ).json()


def test_cutting_lands_in_its_own_pot_and_is_rooting(client):
    stam = _stam(client)
    cutting = client.post(f"/api/plants/{stam['id']}/cutting", json={}).json()

    assert cutting["full_code"] == "WIT01001"  # descendant in the parent's stam
    assert cutting["origin"] == "cutting"
    assert cutting["rooting"] is True
    assert cutting["state"] == "planted"
    assert cutting["location"]["code"] == "B01"  # its own pot


def test_rooting_cutting_cannot_be_split(client):
    stam = _stam(client)
    cutting = client.post(f"/api/plants/{stam['id']}/cutting", json={}).json()
    # Splitting a still-rooting cutting is refused.
    resp = client.post(
        "/api/plants", json={"origin": "split", "parent_plant_id": cutting["id"]}
    )
    assert resp.status_code == 400


def test_transplant_cutting_moves_it_and_ends_rooting(client):
    stam = _stam(client)
    cutting = client.post(f"/api/plants/{stam['id']}/cutting", json={}).json()

    moved = client.post(
        f"/api/plants/{cutting['id']}/transplant",
        json={"new_location_kind": "garden", "new_location_name": "Border"},
    ).json()
    assert moved["rooting"] is False
    assert moved["state"] == "planted"
    assert moved["location"]["code"] == "T01"  # now in the garden, pot lapsed

    # History keeps both the pot and the garden planting.
    detail = client.get(f"/api/plants/{cutting['id']}").json()
    assert len(detail["plantings"]) == 2


def test_only_rooting_cutting_can_be_transplanted(client):
    stam = _stam(client)  # a normal plant, not a rooting cutting
    resp = client.post(
        f"/api/plants/{stam['id']}/transplant",
        json={"new_location_kind": "garden"},
    )
    assert resp.status_code == 400

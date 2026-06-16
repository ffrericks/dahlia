def _variety(client, code):
    return client.post("/api/varieties", json={"code": code, "name": code}).json()


def _planted_plant(client, code, location_id=None, location_name=None):
    """Create a plant and plant it; reuse an existing location if given."""
    v = _variety(client, code)
    p = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": v["id"]}
    ).json()
    # Plant early so fertilize logs (dated mid-June in the tests) fall within the window.
    body = {"plant_id": p["id"], "planted_on": "2026-05-01"}
    if location_id is not None:
        body["location_id"] = location_id
    else:
        body["new_location_kind"] = "container"
        body["new_location_name"] = location_name or "Bak"
    planting = client.post("/api/plantings", json=body).json()
    return p, planting["location_id"]


def test_fertilize_only_entry_is_allowed(client):
    v = _variety(client, "WIT")
    p = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": v["id"]}
    ).json()
    resp = client.post(
        f"/api/plants/{p['id']}/logs",
        json={"fertilized": True, "entry_date": "2026-06-10"},
    )
    assert resp.status_code == 201
    assert resp.json()["fertilized"] is True


def test_last_fertilized_shown_on_plant(client):
    v = _variety(client, "WIT")
    p = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": v["id"]}
    ).json()
    client.post(
        f"/api/plants/{p['id']}/logs",
        json={"fertilized": True, "entry_date": "2026-06-01"},
    )
    client.post(
        f"/api/plants/{p['id']}/logs",
        json={"fertilized": True, "entry_date": "2026-06-20"},
    )
    detail = client.get(f"/api/plants/{p['id']}").json()
    assert detail["last_fertilized"] == "2026-06-20"  # most recent


def test_fertilizing_one_plant_counts_for_others_in_the_same_bak(client):
    a, loc = _planted_plant(client, "WIT", location_name="Houten bak")
    b, _ = _planted_plant(client, "ROO", location_id=loc)  # same bak

    # Only plant A logs the feeding.
    client.post(
        f"/api/plants/{a['id']}/logs",
        json={"fertilized": True, "entry_date": "2026-06-15"},
    )

    # Plant B, sharing the bak, shows the same last-fertilized date.
    assert (
        client.get(f"/api/plants/{b['id']}").json()["last_fertilized"] == "2026-06-15"
    )


def test_plant_in_another_spot_is_not_affected(client):
    a, _ = _planted_plant(client, "WIT", location_name="Bak 1")
    b, _ = _planted_plant(client, "ROO", location_name="Bak 2")  # different spot

    client.post(
        f"/api/plants/{a['id']}/logs",
        json={"fertilized": True, "entry_date": "2026-06-15"},
    )

    assert (
        client.get(f"/api/plants/{a['id']}").json()["last_fertilized"] == "2026-06-15"
    )
    assert client.get(f"/api/plants/{b['id']}").json()["last_fertilized"] is None


def test_same_date_in_one_bak_is_one_feeding(client):
    a, loc = _planted_plant(client, "WIT", location_name="Bak")
    b, _ = _planted_plant(client, "ROO", location_id=loc)

    # Both plants get a "fertilized" entry on the same date — one feeding, not two.
    client.post(
        f"/api/plants/{a['id']}/logs",
        json={"fertilized": True, "entry_date": "2026-06-15"},
    )
    client.post(
        f"/api/plants/{b['id']}/logs",
        json={"fertilized": True, "entry_date": "2026-06-15"},
    )

    # Both simply report that date as last fertilized.
    assert (
        client.get(f"/api/plants/{a['id']}").json()["last_fertilized"] == "2026-06-15"
    )
    assert (
        client.get(f"/api/plants/{b['id']}").json()["last_fertilized"] == "2026-06-15"
    )

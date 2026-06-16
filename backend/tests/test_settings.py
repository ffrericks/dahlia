def test_defaults(client):
    s = client.get("/api/settings").json()
    assert s["auto_fertilize_bak"] is True
    assert s["tool_url"] is None
    assert s["default_garden_name"] is None


def test_update_settings(client):
    updated = client.put(
        "/api/settings",
        json={
            "tool_url": "http://dahlia.local:8000/",
            "default_garden_name": "Achtertuin",
        },
    ).json()
    assert updated["tool_url"] == "http://dahlia.local:8000"  # trailing slash trimmed
    assert updated["default_garden_name"] == "Achtertuin"
    # Persisted
    assert client.get("/api/settings").json()["tool_url"] == "http://dahlia.local:8000"


def test_default_garden_name_used_for_unnamed_spot(client):
    client.put("/api/settings", json={"default_garden_name": "De Border"})
    loc = client.post("/api/locations", json={"kind": "garden"}).json()
    assert loc["name"] == "De Border"
    # An explicit name still wins.
    loc2 = client.post(
        "/api/locations", json={"kind": "garden", "name": "Zijkant"}
    ).json()
    assert loc2["name"] == "Zijkant"


def _bak_with_two_plants(client):
    a = client.post("/api/varieties", json={"code": "WIT", "name": "Wit"}).json()
    b = client.post("/api/varieties", json={"code": "ROO", "name": "Roo"}).json()
    pa = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": a["id"]}
    ).json()
    pb = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": b["id"]}
    ).json()
    loc = client.post(
        "/api/locations", json={"kind": "container", "name": "Bak"}
    ).json()
    # Plant early so the fertilize logs below fall within the planting window.
    client.post(
        "/api/plantings",
        json={
            "plant_id": pa["id"],
            "location_id": loc["id"],
            "planted_on": "2026-05-01",
        },
    )
    client.post(
        "/api/plantings",
        json={
            "plant_id": pb["id"],
            "location_id": loc["id"],
            "planted_on": "2026-05-01",
        },
    )
    return pa, pb


def test_auto_fertilize_off_does_not_share(client):
    pa, pb = _bak_with_two_plants(client)
    client.put("/api/settings", json={"auto_fertilize_bak": False})

    client.post(
        f"/api/plants/{pa['id']}/logs",
        json={"fertilized": True, "entry_date": "2026-06-15"},
    )

    assert (
        client.get(f"/api/plants/{pa['id']}").json()["last_fertilized"] == "2026-06-15"
    )
    # Sharing is off, so the bak-mate is unaffected.
    assert client.get(f"/api/plants/{pb['id']}").json()["last_fertilized"] is None


def test_auto_fertilize_on_shares(client):
    pa, pb = _bak_with_two_plants(client)  # default: sharing on
    client.post(
        f"/api/plants/{pa['id']}/logs",
        json={"fertilized": True, "entry_date": "2026-06-15"},
    )
    assert (
        client.get(f"/api/plants/{pb['id']}").json()["last_fertilized"] == "2026-06-15"
    )

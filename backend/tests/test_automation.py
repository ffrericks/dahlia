def test_automation_summary_has_everything_n8n_needs(client):
    v = client.post(
        "/api/varieties", json={"code": "BUM", "name": "Bumble Rumble"}
    ).json()
    p = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": v["id"]}
    ).json()
    client.post(
        "/api/plantings",
        json={
            "plant_id": p["id"],
            "new_location_kind": "container",
            "new_location_name": "Bak",
        },
    )
    client.post(
        f"/api/plants/{p['id']}/logs",
        json={
            "text": "Eerste bloemen",
            "height_cm": 60,
            "flower_count": 5,
            "entry_date": "2026-06-10",
        },
    )
    client.post(
        f"/api/plants/{p['id']}/logs",
        json={
            "text": "Geoogst en bemest",
            "harvested_count": 3,
            "fertilized": True,
            "entry_date": "2026-06-14",
        },
    )

    rows = client.get("/api/automation/plants").json()
    assert len(rows) == 1
    row = rows[0]
    assert row["full_code"] == "BUM01000"
    assert row["location"] == "B01"
    assert row["height_max_cm"] == 60
    assert row["flowers_peak"] == 5
    assert row["harvested_total"] == 3
    assert row["last_fertilized"] == "2026-06-14"
    assert isinstance(row["days_since_fertilized"], int)
    assert row["last_log_date"] == "2026-06-14"
    assert row["last_log_text"] == "Geoogst en bemest"


def test_automation_hides_gone_plants_by_default(client):
    v = client.post("/api/varieties", json={"code": "WIT", "name": "Wit"}).json()
    p = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": v["id"]}
    ).json()
    client.post(
        f"/api/plants/{p['id']}/dispose",
        json={"kind": "given_away", "recipient": "Jan"},
    )

    assert client.get("/api/automation/plants").json() == []
    assert (
        len(client.get("/api/automation/plants", params={"include_gone": True}).json())
        == 1
    )


def test_automation_handles_plant_without_logs(client):
    v = client.post("/api/varieties", json={"code": "ROO", "name": "Roo"}).json()
    client.post("/api/plants", json={"origin": "purchased", "variety_id": v["id"]})
    row = client.get("/api/automation/plants").json()[0]
    assert row["last_fertilized"] is None
    assert row["days_since_fertilized"] is None
    assert row["harvested_total"] == 0
    assert row["last_log_text"] is None

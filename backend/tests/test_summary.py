def _variety(client, code):
    return client.post("/api/varieties", json={"code": code, "name": code}).json()


def test_summary_downloads_as_text_file(client):
    v = _variety(client, "BUM")
    p = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": v["id"]}
    ).json()

    r = client.get(f"/api/plants/{p['id']}/summary")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")
    assert "attachment" in r.headers["content-disposition"]
    assert "BUM01000" in r.headers["content-disposition"]
    assert "Stamboom & geschiedenis" in r.text


def test_summary_reports_generation_and_line_stats(client):
    v = _variety(client, "BUM")
    root = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": v["id"]}
    ).json()
    child = client.post(
        "/api/plants", json={"origin": "split", "parent_plant_id": root["id"]}
    ).json()

    # Give the line some measurements via a planting + logs.
    client.post(
        "/api/plantings",
        json={
            "plant_id": root["id"],
            "new_location_kind": "garden",
            "planted_on": "2026-05-01",
        },
    )
    client.post(
        f"/api/plants/{root['id']}/logs",
        json={
            "height_cm": 100,
            "flower_count": 12,
            "harvested_count": 4,
            "entry_date": "2026-07-01",
        },
    )

    text = client.get(f"/api/plants/{child['id']}/summary").text
    assert "1e generatie afstammeling" in text  # child is one step from the root
    assert "rond 2026 is gekocht" in text
    assert "Gemiddelde hoogte: 100 cm" in text
    assert "Gemiddeld aantal bloemen (piek): 12" in text
    assert "Verzorging de komende maanden" in text


def test_summary_of_root_says_original(client):
    v = _variety(client, "WIT")
    p = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": v["id"]}
    ).json()
    text = client.get(f"/api/plants/{p['id']}/summary").text
    assert "oorspronkelijke plant" in text

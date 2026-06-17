from datetime import date


def test_cards_count_varieties_plants_and_harvest(client):
    v = client.post("/api/varieties", json={"code": "BUM", "name": "Bumble"}).json()
    p = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": v["id"]}
    ).json()
    client.post(
        f"/api/plants/{p['id']}/logs",
        json={"harvested_count": 4, "entry_date": "2026-07-01"},
    )
    client.post(
        f"/api/plants/{p['id']}/logs",
        json={"harvested_count": 3, "entry_date": "2026-08-01"},
    )

    cards = client.get("/api/dashboard").json()["cards"]
    assert cards["varieties"] == 1
    assert cards["plants"] == 1
    assert cards["harvested_total"] == 7


def test_active_plants_line_reacts_to_disposal(client):
    v = client.post("/api/varieties", json={"code": "WIT", "name": "Wit"}).json()
    a = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": v["id"]}
    ).json()
    client.post("/api/plants", json={"origin": "purchased", "variety_id": v["id"]})

    dash = client.get("/api/dashboard").json()
    year = date.today().year
    month = date.today().month
    current = next(y for y in dash["plants_per_year"] if y["year"] == year)
    assert len(current["points"]) == 12
    assert current["points"][month - 1]["count"] == 2  # both active this month

    # Give one away today -> it drops out of the active count.
    client.post(
        f"/api/plants/{a['id']}/dispose",
        json={"kind": "given_away", "recipient": "Jan"},
    )
    dash = client.get("/api/dashboard").json()
    current = next(y for y in dash["plants_per_year"] if y["year"] == year)
    assert current["points"][month - 1]["count"] == 1


def test_seasons_report_peak_flowers_and_height(client):
    v = client.post("/api/varieties", json={"code": "WIT", "name": "Wit"}).json()
    p = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": v["id"]}
    ).json()
    client.post(
        f"/api/plants/{p['id']}/logs",
        json={
            "flower_count": 8,
            "bud_count": 3,
            "height_cm": 90,
            "entry_date": "2026-07-15",
        },
    )

    seasons = client.get("/api/dashboard").json()["seasons"]
    season = next(s for s in seasons if s["year"] == 2026)
    july = season["points"][6]  # month 7
    assert july["flowers"] == 8
    assert july["buds"] == 3
    assert july["height"] == 90
    assert season["points"][0]["flowers"] is None  # no data in January

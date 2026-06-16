def _variety(client, code):
    return client.post("/api/varieties", json={"code": code, "name": code}).json()


def test_search_by_full_code(client):
    v = _variety(client, "BUM")
    client.post("/api/plants", json={"origin": "purchased", "variety_id": v["id"]})

    hits = client.get("/api/plants/search", params={"q": "BUM01000"}).json()
    assert len(hits) == 1
    assert hits[0]["full_code"] == "BUM01000"


def test_search_is_case_insensitive_and_partial(client):
    v = _variety(client, "BUM")
    client.post("/api/plants", json={"origin": "purchased", "variety_id": v["id"]})
    assert len(client.get("/api/plants/search", params={"q": "bum"}).json()) == 1


def test_search_by_storage_code(client):
    v = _variety(client, "BUM")
    p = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": v["id"]}
    ).json()
    # lift and box it -> composite code BUM01000D0126
    client.post(f"/api/plants/{p['id']}/lift", json={})
    client.put(f"/api/plants/{p['id']}/storage", json={"number": 1, "year": 2026})

    hits = client.get("/api/plants/search", params={"q": "BUM01000D0126"}).json()
    assert len(hits) == 1
    assert hits[0]["storage"]["composite"] == "BUM01000D0126"


def test_search_by_nickname_finds_provisional(client):
    client.post("/api/plants", json={"origin": "unknown", "nickname": "Links"})
    hits = client.get("/api/plants/search", params={"q": "links"}).json()
    assert len(hits) == 1
    assert hits[0]["nickname"] == "Links"


def test_search_finds_disposed_plant(client):
    v = _variety(client, "BUM")
    p = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": v["id"]}
    ).json()
    client.post(f"/api/plants/{p['id']}/dispose", json={"kind": "discarded"})
    # Still findable by an old label even though it's gone from the active list.
    assert len(client.get("/api/plants/search", params={"q": "BUM01000"}).json()) == 1


def test_empty_query_returns_nothing(client):
    assert client.get("/api/plants/search", params={"q": "  "}).json() == []

def make_variety(client, code="WIT", name="Witte Dahlia"):
    return client.post("/api/varieties", json={"code": code, "name": name}).json()


def test_purchased_first_plant_is_01000(client):
    variety = make_variety(client)
    plant = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety["id"]}
    ).json()
    assert plant["number"] == "01000"
    assert plant["full_code"] == "WIT01000"
    assert plant["parent_plant_id"] is None
    assert plant["state"] == "stored"


def test_second_independent_plant_starts_new_stam(client):
    variety = make_variety(client)
    client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety["id"]}
    )
    second = client.post(
        "/api/plants", json={"origin": "gifted", "variety_id": variety["id"]}
    ).json()
    assert second["number"] == "02000"


def test_split_increments_ddd_within_stam(client):
    variety = make_variety(client)
    stam = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety["id"]}
    ).json()

    first_split = client.post(
        "/api/plants", json={"origin": "split", "parent_plant_id": stam["id"]}
    ).json()
    second_split = client.post(
        "/api/plants", json={"origin": "split", "parent_plant_id": stam["id"]}
    ).json()
    # A split of a split stays in the same stam, continuing the DDD counter.
    grandchild = client.post(
        "/api/plants", json={"origin": "split", "parent_plant_id": first_split["id"]}
    ).json()

    assert first_split["number"] == "01001"
    assert second_split["number"] == "01002"
    assert grandchild["number"] == "01003"
    assert grandchild["parent_plant_id"] == first_split["id"]


def test_seedling_creates_new_variety_with_own_01000(client):
    variety = make_variety(client)
    parent = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety["id"]}
    ).json()

    seedling = client.post(
        "/api/plants",
        json={
            "origin": "seedling",
            "parent_plant_id": parent["id"],
            "new_variety_code": "ZAA",
        },
    ).json()
    assert seedling["full_code"] == "ZAA01000"
    assert seedling["variety_code"] == "ZAA"
    assert seedling["parent_plant_id"] == parent["id"]


def test_purchased_can_create_new_variety_inline(client):
    plant = client.post(
        "/api/plants",
        json={
            "origin": "purchased",
            "new_variety_code": "roo",
            "new_variety_name": "Rode",
        },
    ).json()
    assert plant["full_code"] == "ROO01000"


def test_split_requires_parent(client):
    response = client.post("/api/plants", json={"origin": "split"})
    assert response.status_code == 422


def test_seedling_requires_new_variety_code(client):
    variety = make_variety(client)
    parent = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety["id"]}
    ).json()
    response = client.post(
        "/api/plants", json={"origin": "seedling", "parent_plant_id": parent["id"]}
    )
    assert response.status_code == 422


def test_tree_and_summary(client):
    variety = make_variety(client)
    stam = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety["id"]}
    ).json()
    client.post("/api/plants", json={"origin": "split", "parent_plant_id": stam["id"]})

    tree = client.get("/api/plants/tree").json()
    assert len(tree) == 1  # one root
    assert tree[0]["full_code"] == "WIT01000"
    assert len(tree[0]["children"]) == 1
    assert tree[0]["children"][0]["full_code"] == "WIT01001"

    summary = client.get("/api/plants/summary").json()
    assert summary["total"] == 2
    assert summary["by_state"]["stored"] == 2


def test_cannot_delete_plant_with_descendants(client):
    variety = make_variety(client)
    stam = client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety["id"]}
    ).json()
    client.post("/api/plants", json={"origin": "split", "parent_plant_id": stam["id"]})

    assert client.delete(f"/api/plants/{stam['id']}").status_code == 409


def test_cannot_delete_variety_with_plants(client):
    variety = make_variety(client)
    client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety["id"]}
    )
    assert client.delete(f"/api/varieties/{variety['id']}").status_code == 409

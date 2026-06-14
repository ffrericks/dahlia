def _plant(client, code="WIT"):
    variety = client.post("/api/varieties", json={"code": code, "name": "Wit"}).json()
    return client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety["id"]}
    ).json()


def test_discard_hides_from_active_list_but_keeps_in_tree(client):
    plant = _plant(client)
    disposed = client.post(
        f"/api/plants/{plant['id']}/dispose", json={"kind": "discarded", "reason": "Verrot"}
    )
    assert disposed.status_code == 200
    assert disposed.json()["state"] == "discarded"

    # Gone from the active list...
    assert client.get("/api/plants").json() == []
    # ...but still listable with include_gone, and still in the tree.
    assert len(client.get("/api/plants", params={"include_gone": True}).json()) == 1
    assert len(client.get("/api/plants/tree").json()) == 1


def test_give_away_stores_recipient(client):
    plant = _plant(client)
    client.post(
        f"/api/plants/{plant['id']}/dispose",
        json={"kind": "given_away", "recipient": "Buurvrouw Ans"},
    )
    detail = client.get(f"/api/plants/{plant['id']}").json()
    assert detail["state"] == "given_away"
    assert detail["disposal"]["recipient"] == "Buurvrouw Ans"


def test_disease_discard_sets_warning(client):
    plant = _plant(client)
    client.post(
        f"/api/plants/{plant['id']}/dispose",
        json={"kind": "discarded", "reason": "Dahlia-gal", "disease_warning": True},
    )
    detail = client.get(f"/api/plants/{plant['id']}").json()
    assert detail["disease_warning"] is True
    assert detail["disposal"]["disease_warning"] is True


def test_disposing_a_planted_plant_frees_the_spot(client):
    plant = _plant(client)
    client.post(
        "/api/plantings",
        json={"plant_id": plant["id"], "new_location_kind": "garden", "new_location_name": "Border"},
    )
    client.post(f"/api/plants/{plant['id']}/dispose", json={"kind": "discarded"})

    detail = client.get(f"/api/plants/{plant['id']}").json()
    assert detail["location"] is None
    assert detail["plantings"][0]["lifted_on"] is not None  # season closed


def test_not_emerged_counts_as_discarded_with_note(client):
    plant = _plant(client)
    client.post(
        "/api/plantings",
        json={"plant_id": plant["id"], "new_location_kind": "garden"},
    )
    response = client.post(f"/api/plants/{plant['id']}/not-emerged")
    assert response.status_code == 200
    assert response.json()["state"] == "discarded"

    detail = client.get(f"/api/plants/{plant['id']}").json()
    assert detail["disposal"]["reason"] == "Niet opgekomen"
    assert any("Niet opgekomen" in (log["text"] or "") for log in detail["logs"])


def test_cannot_dispose_twice(client):
    plant = _plant(client)
    client.post(f"/api/plants/{plant['id']}/dispose", json={"kind": "discarded"})
    again = client.post(f"/api/plants/{plant['id']}/dispose", json={"kind": "given_away"})
    assert again.status_code == 400


def test_descendant_tally_counts_owned_vs_total(client):
    parent = _plant(client)
    # Two splits, then give one away.
    s1 = client.post("/api/plants", json={"origin": "split", "parent_plant_id": parent["id"]}).json()
    client.post("/api/plants", json={"origin": "split", "parent_plant_id": parent["id"]})
    client.post(f"/api/plants/{s1['id']}/dispose", json={"kind": "given_away", "recipient": "Jan"})

    tally = client.get(f"/api/plants/{parent['id']}").json()["descendants"]
    assert tally["total"] == 2
    assert tally["owned"] == 1

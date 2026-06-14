def _plant(client, code="WIT"):
    variety = client.post("/api/varieties", json={"code": code, "name": "Wit"}).json()
    return client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety["id"]}
    ).json()


def test_add_and_list_log_entries(client):
    plant = _plant(client)
    created = client.post(
        f"/api/plants/{plant['id']}/logs",
        json={"text": "Mooi gegroeid", "height_cm": 45, "bud_count": 8, "flower_count": 3, "harvested_count": 1},
    )
    assert created.status_code == 201
    assert created.json()["height_cm"] == 45

    detail = client.get(f"/api/plants/{plant['id']}").json()
    assert len(detail["logs"]) == 1
    assert detail["logs"][0]["flower_count"] == 3


def test_empty_log_entry_is_rejected(client):
    plant = _plant(client)
    response = client.post(f"/api/plants/{plant['id']}/logs", json={})
    assert response.status_code == 422


def test_negative_metric_is_rejected(client):
    plant = _plant(client)
    response = client.post(f"/api/plants/{plant['id']}/logs", json={"height_cm": -5})
    assert response.status_code == 422


def test_delete_log_entry(client):
    plant = _plant(client)
    log = client.post(f"/api/plants/{plant['id']}/logs", json={"text": "x"}).json()
    assert client.delete(f"/api/plants/{plant['id']}/logs/{log['id']}").status_code == 204
    assert client.get(f"/api/plants/{plant['id']}").json()["logs"] == []

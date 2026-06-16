import io

from PIL import Image


def _image_bytes(color=(200, 30, 30)):
    img = Image.new("RGB", (60, 40), color)
    buffer = io.BytesIO()
    img.save(buffer, "PNG")
    return buffer.getvalue()


def _make_plant(client):
    variety = client.post("/api/varieties", json={"code": "WIT", "name": "Wit"}).json()
    return client.post(
        "/api/plants", json={"origin": "purchased", "variety_id": variety["id"]}
    ).json()


def test_first_photo_becomes_profile(client):
    plant = _make_plant(client)
    response = client.post(
        f"/api/plants/{plant['id']}/photos",
        files={"file": ("flower.png", _image_bytes(), "image/png")},
    )
    assert response.status_code == 201
    photo = response.json()
    assert photo["is_profile"] is True
    assert photo["thumbnail_url"].startswith("/media/")


def test_non_image_is_rejected(client):
    plant = _make_plant(client)
    response = client.post(
        f"/api/plants/{plant['id']}/photos",
        files={"file": ("notes.txt", b"this is not an image", "text/plain")},
    )
    assert response.status_code == 400


def test_profile_photo_becomes_variety_image(client):
    plant = _make_plant(client)
    client.post(
        f"/api/plants/{plant['id']}/photos",
        files={"file": ("flower.png", _image_bytes(), "image/png")},
    )
    variety = client.get("/api/varieties").json()[0]
    assert variety["image_thumbnail"] is not None
    assert variety["plant_count"] == 1


def test_set_profile_and_delete(client):
    plant = _make_plant(client)
    first = client.post(
        f"/api/plants/{plant['id']}/photos",
        files={"file": ("a.png", _image_bytes((10, 10, 200)), "image/png")},
    ).json()
    second = client.post(
        f"/api/plants/{plant['id']}/photos",
        files={"file": ("b.png", _image_bytes((10, 200, 10)), "image/png")},
    ).json()

    # Make the second photo the profile, then confirm the switch.
    client.put(f"/api/plants/{plant['id']}/photos/{second['id']}/profile")
    detail = client.get(f"/api/plants/{plant['id']}").json()
    profiles = {p["id"]: p["is_profile"] for p in detail["photos"]}
    assert profiles[second["id"]] is True
    assert profiles[first["id"]] is False

    # Deleting the profile photo promotes the remaining one.
    assert (
        client.delete(f"/api/plants/{plant['id']}/photos/{second['id']}").status_code
        == 204
    )
    detail = client.get(f"/api/plants/{plant['id']}").json()
    assert len(detail["photos"]) == 1
    assert detail["photos"][0]["is_profile"] is True

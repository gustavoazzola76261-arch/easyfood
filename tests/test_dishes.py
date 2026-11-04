from io import BytesIO

from PIL import Image

from tests.conftest import auth_header, register_and_login


def _png():
    buffer = BytesIO()
    Image.new("RGB", (40, 20), "red").save(buffer, format="PNG")
    return buffer.getvalue()


def _create_owned_restaurant(client):
    token, user = register_and_login(client)
    restaurant = client.post(
        "/restaurants",
        json={"name": "Cantina da Nona", "category": "Italiana", "rating": 4.7},
        headers=auth_header(token),
    ).get_json()
    return token, user, restaurant


def test_create_and_list_dishes(client):
    token, _user, restaurant = _create_owned_restaurant(client)
    response = client.post(
        f"/restaurants/{restaurant['id']}/dishes",
        json={
            "name": "Pizza Margherita",
            "description": "Molho de tomate, queijo e manjericão",
            "price": 49.90,
            "portion": "450g",
            "kind": "prato",
        },
        headers=auth_header(token),
    )
    assert response.status_code == 201
    dish = response.get_json()
    assert dish["name"] == "Pizza Margherita"
    assert dish["restaurantId"] == restaurant["id"]
    assert dish["imageUrl"] is None

    listed = client.get(f"/restaurants/{restaurant['id']}/dishes")
    assert listed.status_code == 200
    assert len(listed.get_json()) == 1


def test_create_dish_requires_login(client):
    token, _user, restaurant = _create_owned_restaurant(client)
    response = client.post(
        f"/restaurants/{restaurant['id']}/dishes",
        json={"name": "Pizza", "description": "Massa", "price": 10},
    )
    assert response.status_code == 401


def test_stranger_cannot_create_dish(client):
    token, _user, restaurant = _create_owned_restaurant(client)
    other_token, _other = register_and_login(client, "Beto", "beto@easyfood.com")
    response = client.post(
        f"/restaurants/{restaurant['id']}/dishes",
        json={"name": "Pizza", "description": "Massa", "price": 10},
        headers=auth_header(other_token),
    )
    assert response.status_code == 403


def test_upload_dish_image(client):
    token, _user, restaurant = _create_owned_restaurant(client)
    dish = client.post(
        f"/restaurants/{restaurant['id']}/dishes",
        json={"name": "Pizza Margherita", "description": "Clássica", "price": 49.9},
        headers=auth_header(token),
    ).get_json()

    upload = client.post(
        f"/dishes/{dish['id']}/image",
        data={"image": (BytesIO(_png()), "foto.png")},
        headers=auth_header(token),
    )
    assert upload.status_code == 200
    body = upload.get_json()
    assert body["imageUrl"].startswith("/uploads/dishes/")
    assert body["imageUrl"].endswith(".webp")

    image = client.get(body["imageUrl"])
    assert image.status_code == 200


def test_upload_rejects_non_image(client):
    token, _user, restaurant = _create_owned_restaurant(client)
    dish = client.post(
        f"/restaurants/{restaurant['id']}/dishes",
        json={"name": "Suco", "description": "Laranja", "price": 8, "kind": "bebida", "portion": "300ml"},
        headers=auth_header(token),
    ).get_json()
    upload = client.post(
        f"/dishes/{dish['id']}/image",
        data={"image": (BytesIO(b"nao-e-imagem"), "nota.txt")},
        headers=auth_header(token),
    )
    assert upload.status_code == 400
    listed = client.get(f"/restaurants/{restaurant['id']}/dishes").get_json()
    assert listed[0]["imageUrl"] is None


def test_upload_without_file(client):
    token, _user, restaurant = _create_owned_restaurant(client)
    dish = client.post(
        f"/restaurants/{restaurant['id']}/dishes",
        json={"name": "Pudim", "description": "Leite", "price": 12, "kind": "sobremesa"},
        headers=auth_header(token),
    ).get_json()
    upload = client.post(
        f"/dishes/{dish['id']}/image",
        headers=auth_header(token),
    )
    assert upload.status_code == 400

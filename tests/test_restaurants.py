from tests.conftest import auth_header, register_and_login


def _auth_token(client):
    token, _user = register_and_login(client)
    return token


def test_list_restaurants_is_public(client):
    response = client.get("/restaurants")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_restaurant_requires_login(client):
    response = client.post(
        "/restaurants",
        json={"name": "Taco Loco", "category": "Mexicana", "rating": 4.2},
    )
    assert response.status_code == 401
    assert "Token" in response.get_json()["error"]


def test_create_restaurant_rejects_invalid_token(client):
    response = client.post(
        "/restaurants",
        json={"name": "Taco Loco", "category": "Mexicana", "rating": 4.2},
        headers={"Authorization": "Bearer token-invalido"},
    )
    assert response.status_code == 401


def test_create_restaurant_with_login(client):
    token = _auth_token(client)
    response = client.post(
        "/restaurants",
        json={"name": "Taco Loco", "category": "Mexicana", "rating": 4.2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == "Taco Loco"
    assert body["category"] == "Mexicana"

    listed = client.get("/restaurants").get_json()
    assert len(listed) == 1
    assert listed[0]["name"] == "Taco Loco"
    assert listed[0]["ownerId"] is not None


def test_create_restaurant_requires_name_and_category(client):
    token = _auth_token(client)
    response = client.post(
        "/restaurants",
        json={"rating": 4.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400

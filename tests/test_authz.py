from tests.conftest import auth_header, register_and_login


def test_owner_can_add_gerente_and_gerente_can_edit_menu(client):
    owner_token, _owner = register_and_login(client, "Ana", "ana@easyfood.com")
    gerente_token, _gerente = register_and_login(client, "Gina", "gina@easyfood.com")
    restaurant = client.post(
        "/restaurants",
        json={"name": "Casa da Ana", "category": "Brasileira"},
        headers=auth_header(owner_token),
    ).get_json()

    added = client.post(
        f"/restaurants/{restaurant['id']}/staff",
        json={"email": "gina@easyfood.com", "role": "gerente"},
        headers=auth_header(owner_token),
    )
    assert added.status_code == 201

    dish = client.post(
        f"/restaurants/{restaurant['id']}/dishes",
        json={"name": "Feijoada", "description": "Completa", "price": 38},
        headers=auth_header(gerente_token),
    )
    assert dish.status_code == 201

    deleted = client.delete(
        f"/restaurants/{restaurant['id']}/dishes/{dish.get_json()['id']}",
        headers=auth_header(gerente_token),
    )
    assert deleted.status_code == 200


def test_atendente_cannot_edit_menu_but_can_see_orders(client):
    owner_token, _owner = register_and_login(client, "Ana", "ana@easyfood.com")
    attendant_token, _att = register_and_login(client, "Leo", "leo@easyfood.com")
    restaurant = client.post(
        "/restaurants",
        json={"name": "Casa da Ana", "category": "Brasileira"},
        headers=auth_header(owner_token),
    ).get_json()
    client.post(
        f"/restaurants/{restaurant['id']}/staff",
        json={"email": "leo@easyfood.com", "role": "atendente"},
        headers=auth_header(owner_token),
    )

    denied = client.post(
        f"/restaurants/{restaurant['id']}/dishes",
        json={"name": "Coxinha", "description": "Frango", "price": 8},
        headers=auth_header(attendant_token),
    )
    assert denied.status_code == 403

    staff_denied = client.post(
        f"/restaurants/{restaurant['id']}/staff",
        json={"email": "ana@easyfood.com", "role": "gerente"},
        headers=auth_header(attendant_token),
    )
    assert staff_denied.status_code == 403

    orders = client.get(
        f"/restaurants/{restaurant['id']}/orders",
        headers=auth_header(attendant_token),
    )
    assert orders.status_code == 200
    assert len(orders.get_json()) >= 1


def test_mine_includes_owned_and_staff_restaurants(client):
    owner_token, _owner = register_and_login(client, "Ana", "ana@easyfood.com")
    staff_token, _staff = register_and_login(client, "Gina", "gina@easyfood.com")
    restaurant = client.post(
        "/restaurants",
        json={"name": "Casa da Ana", "category": "Brasileira"},
        headers=auth_header(owner_token),
    ).get_json()
    client.post(
        f"/restaurants/{restaurant['id']}/staff",
        json={"email": "gina@easyfood.com", "role": "gerente"},
        headers=auth_header(owner_token),
    )

    mine = client.get("/restaurants/mine", headers=auth_header(staff_token))
    assert mine.status_code == 200
    body = mine.get_json()
    assert len(body) == 1
    assert body[0]["role"] == "gerente"


def test_search_restaurants(client):
    token, _user = register_and_login(client)
    client.post(
        "/restaurants",
        json={"name": "Burger House", "category": "Burger"},
        headers=auth_header(token),
    )
    client.post(
        "/restaurants",
        json={"name": "Sushi House", "category": "Sushi"},
        headers=auth_header(token),
    )
    found = client.get("/restaurants?q=sushi")
    assert found.status_code == 200
    names = [item["name"] for item in found.get_json()]
    assert names == ["Sushi House"]

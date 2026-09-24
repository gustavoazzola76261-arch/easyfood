def test_register_creates_user(client):
    response = client.post(
        "/auth/register",
        json={"name": "Ana", "email": "ana@easyfood.com", "password": "senha123"},
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["email"] == "ana@easyfood.com"
    assert "password" not in body


def test_register_rejects_missing_fields(client):
    response = client.post("/auth/register", json={"email": "x@y.com"})
    assert response.status_code == 400


def test_register_rejects_duplicate_email(client):
    payload = {"name": "Ana", "email": "ana@easyfood.com", "password": "senha123"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409


def test_login_returns_jwt(client):
    client.post(
        "/auth/register",
        json={"name": "Ana", "email": "ana@easyfood.com", "password": "senha123"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "ana@easyfood.com", "password": "senha123"},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert "token" in body
    assert body["user"]["email"] == "ana@easyfood.com"


def test_login_rejects_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        json={"email": "naoexiste@easyfood.com", "password": "errada"},
    )
    assert response.status_code == 401


def test_me_requires_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_valid_token(client):
    client.post(
        "/auth/register",
        json={"name": "Ana", "email": "ana@easyfood.com", "password": "senha123"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "ana@easyfood.com", "password": "senha123"},
    )
    token = login.get_json()["token"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.get_json()["user"]["email"] == "ana@easyfood.com"

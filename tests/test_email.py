from tests.conftest import auth_header, register_and_login


def test_email_failure_does_not_block_restaurant_create(client, monkeypatch):
    def boom(**_kwargs):
        raise RuntimeError("Falha simulada no envio de e-mail")

    monkeypatch.setattr("src.modules.shared.email_service.send_email", boom)

    token, _user = register_and_login(client)
    response = client.post(
        "/restaurants",
        json={"name": "Cantina da Nona", "category": "Italiana", "rating": 4.7},
        headers=auth_header(token),
    )
    assert response.status_code == 201
    listed = client.get("/restaurants").get_json()
    assert any(item["name"] == "Cantina da Nona" for item in listed)


def test_send_email_console_mode_does_not_raise():
    from src.modules.shared.email_service import send_email

    send_email(
        to="teste@easyfood.com",
        to_name="Teste",
        subject="Olá",
        header="Header",
        body="Corpo",
        footer="Rodapé",
    )

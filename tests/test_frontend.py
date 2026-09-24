def test_home_serves_frontend(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "EasyFood" in html
    assert "Inscreva-se" in html
    assert "Sair" in html
    assert "Cadastrar Restaurante" in html

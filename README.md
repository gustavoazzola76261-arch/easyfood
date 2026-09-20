# EasyFood

API e frontend de delivery educacional (disciplina Software Architecture & Design Patterns), implementados em **Python/Flask** com evolução documentada em ADRs.

## Como rodar

```bash
pip install -r requirements.txt
copy .env.example .env   # Windows
python server.py
```

Abra [http://localhost:3000](http://localhost:3000).

## Endpoints

| Método | Rota | Auth |
|--------|------|------|
| GET | `/restaurants` | público |
| POST | `/restaurants` | Bearer JWT |
| POST | `/auth/register` | público |
| POST | `/auth/login` | público |
| GET | `/auth/me` | Bearer JWT |

## Evolução (commits / ADRs)

1. ADR-001 — Stack Python/Flask + `GET /restaurants`
2. ADR-002 — `POST /restaurants` em memória
3. ADR-003 — Persistência SQLAlchemy/SQLite
4. ADR-004 — Arquitetura em camadas
5. ADR-005 — Autenticação JWT
6. ADR-006 — Integração do frontend

## Estrutura

```
server.py
src/
  app.py
  database/
  modules/
    auth/
    restaurants/
public/
  index.html
ADR-00X.md
```

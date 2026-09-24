# EasyFood

A EasyFood é um app educacional de **delivery**: o usuário consulta restaurantes, cria uma conta, faz login e só então cadastra novos estabelecimentos. O projeto replica o contrato HTTP das aulas de Software Architecture & Design Patterns, implementado em **Python/Flask**, com as decisões técnicas registradas em ADRs.

Fluxo do frontend:

1. Tela de **login** (entrada da aplicação)
2. **Inscreva-se** para criar uma conta de usuário (e voltar ao login)
3. Após o login, lista de restaurantes e cadastro de restaurantes
4. **Sair** encerra a sessão; sem JWT não é possível cadastrar restaurante (nem pela API)

Persistência: **PostgreSQL** (`easyfood`) via SQLAlchemy + `psycopg2`. Os testes e o GitHub Actions usam SQLite em memória.

## Como executar

Pré-requisitos: Python 3.11+ e PostgreSQL com o banco `easyfood` criado.

1. Clone o repositório e entre na pasta do projeto.
2. Crie um ambiente virtual (recomendado) e instale as dependências:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Copie o arquivo de ambiente e ajuste usuário/senha se necessário:

```bash
copy .env.example .env
```

Valores esperados em `.env`:

```
DATABASE_URL=postgresql+psycopg2://postgres:1234@localhost:5432/easyfood
JWT_SECRET=troque-por-uma-chave-longa-e-aleatoria
```

4. Suba o servidor:

```bash
python server.py
```

5. Abra [http://localhost:3000](http://localhost:3000).

Sem PostgreSQL local, descomente no `.env` a linha SQLite:

```
DATABASE_URL=sqlite:///easyfood.db
```

## Testes

```bash
pytest tests/ -v
```

No GitHub, o workflow `.github/workflows/tests.yml` instala as dependências e executa o mesmo comando em cada push/PR.

## Endpoints

| Método | Rota | Auth |
|--------|------|------|
| GET | `/restaurants` | público |
| POST | `/restaurants` | Bearer JWT |
| POST | `/auth/register` | público |
| POST | `/auth/login` | público |
| GET | `/auth/me` | Bearer JWT |

## Evolução (commits / ADRs)

Documentos em `ADRs/`:

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
tests/
ADRs/
.github/workflows/tests.yml
```

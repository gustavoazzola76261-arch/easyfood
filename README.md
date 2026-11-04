# EasyFood

A EasyFood é um app educacional de **delivery**: o usuário consulta restaurantes, cria uma conta, faz login e pode cadastrar o próprio estabelecimento. Dono e gerente gerenciam o **cardápio** (com imagem otimizada); o atendente só vê **pedidos**. Confirmações de conta, restaurante e prato saem pelo serviço compartilhado de e-mail.

O projeto replica o contrato HTTP das aulas de Software Architecture & Design Patterns, em **Python/Flask**, com decisões registradas em ADRs.

## Fluxo do app

1. **Login** (entrada). **Inscreva-se** cria a conta e volta ao login.
2. **Início**: lista de restaurantes e cardápio público.
3. **Buscar**: procura restaurante por nome ou categoria.
4. **Perfil**: dados da conta, cadastro de restaurante e **Sair**.
5. **Restaurante** (só aparece se a pessoa for dona ou da equipe):
   - dono: imagem, cardápio, funcionários (gerente/atendente) e pedidos
   - gerente: cardápio e pedidos
   - atendente: somente pedidos

Sem JWT não dá para criar restaurante nem alterar cardápio. Sem papel de dono/gerente não dá para mudar pratos.

## Como executar

Pré-requisitos: Python 3.11+ e PostgreSQL com o banco `easyfood` (ou SQLite no `.env`).

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python server.py
```

Abra [http://localhost:3000](http://localhost:3000).

E-mail: sem `EMAIL_API_KEY` a confirmação aparece no terminal. Com chave Resend, o envio vai para a API. Imagens otimizadas ficam em `uploads/`.

## Testes

```bash
pytest tests/ -v
```

O GitHub Actions (`.github/workflows/tests.yml`) roda o mesmo comando em SQLite.

## Endpoints

| Método | Rota | Quem |
|--------|------|------|
| GET | `/restaurants` | público (`?q=` busca) |
| GET | `/restaurants/mine` | JWT |
| GET | `/restaurants/:id` | público |
| POST | `/restaurants` | JWT (vira dono) |
| PATCH | `/restaurants/:id` | dono |
| POST | `/restaurants/:id/image` | dono |
| GET/POST | `/restaurants/:id/staff` | dono |
| DELETE | `/restaurants/:id/staff/:userId` | dono |
| GET | `/restaurants/:id/orders` | dono, gerente, atendente |
| GET | `/restaurants/:id/dishes` | público |
| POST/DELETE | `/restaurants/:id/dishes` | dono ou gerente |
| POST | `/dishes/:id/image` | dono ou gerente |
| POST | `/auth/register` | público |
| POST | `/auth/login` | público |
| GET | `/auth/me` | JWT |

## Evolução (ADRs)

1. ADR-001 — Stack Python/Flask
2. ADR-002 — `POST /restaurants` em memória
3. ADR-003 — Persistência
4. ADR-004 — Arquitetura em camadas
5. ADR-005 — Autenticação JWT
6. ADR-006 — Frontend
7. ADR-007 — E-mail compartilhado
8. ADR-008 — Imagens na própria API
9. ADR-009 — Papéis por restaurante

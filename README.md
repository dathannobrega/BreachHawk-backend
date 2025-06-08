# 🛡️ BreachHawk — Plataforma de Threat Intelligence na Dark Web

Este backend agora utiliza totalmente o **Django** e o **Django REST Framework** para prover a API de monitoramento de vazamentos.
```bash
cd backend/django_project
python manage.py runserver
```

---

### 📁 Estrutura do projeto Django

```
backend/django_project
├── manage.py
├── breachhawk/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── urls.py
├── billing/
│   └── ...
├── companies/
│   └── ...
├── leaks/
│   └── ...
├── notifications/
│   └── ...
├── scrapers/
│   └── ...
├── sites/
│   └── ...
└── templates/
    └── emails/
├── utils/
│   └── common helpers like TOR circuit renewal
```

---

### 📁 Estrutura inicial do repositório (MVP v0.1)

```text
.
├── .env
├── .gitignore
├── docker-compose.yml
├── README.md
├── test_main.http
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── init_db.py
│       ├── api/
│       │   └── v1/
│       │       ├── deps.py
│       │       └── routers/
│       │           ├── auth.py
│       │           ├── leaks.py
│       │           └── sites.py
│       ├── core/
│       │   ├── config.py
│       │   ├── jwt.py
│       │   ├── logging_conf.py
│       │   └── security.py
│       ├── db/
│       │   ├── base.py
│       │   ├── session.py
│       │   └── models/
│       │       └── user.py
│       ├── schemas/
│       │   └── auth.py
│       ├── services/
│       │   └── auth_service.py
│       ├── repository/
│       ├── tasks/
│       └── tests/
├── proxy/
│   └── tor/
│       ├── Dockerfile
│       └── torrc
├── scraper/
│   ├── adapters/
│   │   ├── bs_adapter.py
│   │   ├── requests_adapter.py
│   │   └── selenium_adapter.py
│   └── captcha_solvers/
└── worker/
    └── Dockerfile
```

---

### 🧱 Arquitetura

* **Django + PostgreSQL + Celery**
* **Clean Architecture**: separação entre `api`, `services`, `repository`, `db`, `schemas`.
* **Django + PostgreSQL + Celery**
* **Segurança**:

  * Autenticação via JWT
  * Variáveis de ambiente isoladas por `.env`
  * Acesso a `.onion` somente via proxy TOR (`torsocks`)
* **Frontend**:

  * Next.js com autenticação integrada via token JWT
  * Estrutura baseada em páginas, estados e contexto global de login

---

### 🐳 Serviços no `docker-compose.yml`

| Serviço       | Descrição                                   |
| ------------- | ------------------------------------------- |
| **backend**   | API Django com Gunicorn                     |
| **db**        | PostgreSQL persistente                      |
| **mongo**     | Banco NoSQL para armazenar leaks            |
| **worker**    | Celery worker (para scraping assíncrono)    |
| **redis**     | Broker do Celery                            |
| **tor-proxy** | Proxy SOCKS5 para navegação `.onion` segura |

---

### 🔐 Fluxo de autenticação

1. `POST /api/v1/auth/register` → Criação de usuário
2. `POST /api/v1/auth/login` → JWT
3. `GET /api/v1/auth/me` → Requisição autenticada com `Bearer <token>`
4. `GET /api/v1/auth/sessions` → Lista sessões do usuário (inclui device e localização)
5. `GET /api/v1/auth/login-history` → Histórico de logins (device, IP, localização e sucesso)

---

### 🧾 Entidades principais

| Tabela      | Campos principais                  | Função                        |
| ----------- | ---------------------------------- | ----------------------------- |
| `users`     | `id`, `email`, `hashed_password`   | Autenticação                  |
| `sites`     | `url`, `auth_type`, `captcha_type` | Portais da dark web           |
| `leaks`     | `empresa`, `pais`, `data`, `fonte` | Vazamentos encontrados        |
| `tasks_log` | `site_id`, `status`, `timestamp`   | Histórico de coletas/scraping |

---

### 🧪 Testes

* Testes em `pytest` para endpoints e lógicas de autenticação
* Arquivo `test_main.http` disponível para testes manuais via REST Client

---

### 📈 Roadmap v0.2+

* [ ] OAuth 2.0 com escopo RBAC
* [ ] Templates de resolução de CAPTCHA (manual + automático via OCR)
* [ ] Painel interativo com dashboard de vazamentos
* [ ] Detecção de anomalias e clusters de vazamentos
* [ ] Hardening: CIS Benchmarks, security headers, audit logs
* [ ] CI/CD com Docker + Testes automatizados
* [ ] Helm Chart para deploy em Kubernetes (HA)

---

### ✅ Critérios para versão `v0.1`

| Funcionalidade     | Status                      |
| ------------------ | --------------------------- |
| Autenticação JWT   | ✅ Concluído                 |
| Cadastro de sites  | 🟡 Em andamento             |
| Scraping agendado  | 🟡 Estrutura inicial pronta |
| Integração TOR     | 🟢 Docker configurado       |
| Interface frontend | 🟡 Login funcional          |
| Testes iniciais    | 🟡 Base para API criada     |

---
Arquivos que agora contêm cada peça
Arquivo	Responsabilidade
backend/django_project/scrapers/base.py	Classe‐base + registry (já mostrado).
backend/django_project/scrapers/akira_cli.py	Plugin específico com import tardio de Leak.
backend/django_project/breachhawk/celery.py	Dispatcher e tarefas Celery.
backend/api/v1/routers/sites.py	Endpoints /sites, /sites/{id}/run, /sites/tasks/{task} que chamam a task Celery.

5 . Fluxo final
POST /sites grava scraper="akira_cli" na tabela sites.

POST /sites/{id}/run → scrape_site.delay(id)

Worker Celery executa o dispatcher → chama registry["akira_cli"]

AkiraCLIScraper.scrape() faz Playwright + Tor → grava leaks

GET /sites/tasks/{task_id} devolve {"inserted": X}

---
Iniciar:
```bash
alembic revision --autogenerate -m "first commit"
alembic upgrade head
```
TOda vez que mudar algum model:
```bash
alembic revision --autogenerate -m "first commit"
alembic upgrade head
```
## Password Policy API

Endpoint público para consulta da política de senha.

- `GET /api/v1/password-policy/public`

Exemplo de resposta:

```json
{
  "min_length": 8,
  "require_uppercase": true,
  "require_lowercase": true,
  "require_numbers": true,
  "require_symbols": true
}
```
## Billing API

Os endpoints de faturamento expõem dados do Stripe e requerem token de usuário com funcção `platform_admin`.

- `GET /api/v1/billing/invoices`
- `GET /api/v1/billing/payments`
- `GET /api/v1/billing/subscriptions`


# BreachHawk Backend

BreachHawk é uma plataforma de threat intelligence especializada em identificar e monitorar vazamentos divulgados na dark web. Este repositório contém o serviço backend responsável por expor as APIs, executar tarefas de scraping e notificar os usuários sobre novos incidentes.

## Tecnologias Utilizadas
- **Python 3.12**
- **Django 5** e **Django REST Framework** para construção das APIs REST
- **Celery** e **Redis** para tarefas assíncronas e filas
- **PostgreSQL** como banco relacional principal
- **MongoDB** para armazenamento dos dumps de vazamentos
- **Stripe** para faturamento e gestão de assinaturas
- **Docker** e **docker-compose** para orquestração dos serviços

## Principais Funcionalidades
- Registro de usuários, autenticação JWT e login com Google
- Gestão de empresas, planos de assinatura e faturamento via Stripe
- Coleta de dados em fontes da dark web através de scrapers e workers Celery
- Painel administrativo para gestão de sites monitorados e logs de scraping
- Envio de notificações de vazamentos por e‑mail

## Estrutura do Repositório
```
backend/
├── requirements.txt
└── django_project/
    ├── manage.py
    ├── breachhawk/          # configurações do projeto
    ├── accounts/            # autenticação e sessões
    ├── billing/             # integração com Stripe
    ├── companies/           # empresas e planos
    ├── leaks/               # modelo de vazamentos (MongoDB)
    ├── notifications/       # configuração de SMTP
    ├── scrapers/            # scrapers e tasks Celery
    ├── sites/               # sites monitorados
    └── utils/               # utilitários diversos
proxy/tor/      # container TOR para acesso .onion
scraper/        # adapters legados de scraping
worker/         # imagem do worker Celery
```

## Configuração e Execução

1. Criar e ativar um ambiente virtual.
2. Instalar dependências:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Copiar o arquivo `.env.example` para `.env` e ajustar as variáveis necessárias (PostgreSQL, MongoDB, Redis, SMTP, Stripe etc.).
4. Aplicar migrações e criar um superusuário:
   ```bash
   cd backend/django_project
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. Iniciar o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```

### Executando com Docker
Para subir todos os serviços (API, MongoDB, Redis, TOR, worker Celery etc.):

```bash
docker-compose up --build
```

A API ficará disponível em `http://localhost:8000/api/`.

## Endpoints Principais

- `POST /api/accounts/register` – cria um usuário
- `POST /api/accounts/login` – autenticação e geração de JWT
- `GET /api/accounts/login/google` – login via conta Google
- `GET /api/accounts/me` – dados do usuário autenticado
- `GET /api/companies/companies` – CRUD de empresas (admin)
- `GET /api/companies/plans` – planos de assinatura (admin)
- `GET /api/leaks/leaks` – lista ou cria vazamentos
- `GET /api/sites/` – gerenciamento de sites monitorados (admin)
- `GET /api/scrapers/logs` – logs de scraping (admin)
- `GET /api/billing/invoices` – faturas no Stripe (admin)
- `GET /api/notifications/smtp` – configurações de e‑mail

Todos os endpoints estão sob o prefixo `/api/`.

## Testes

Após instalar as dependências principais, instale os pacotes de desenvolvimento e execute os testes com `pytest`:

```bash
pip install -r requirements-dev.txt
pytest -q
```


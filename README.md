# BreachHawk Backend

Plataforma de intelligence focada em vazamentos na dark web. O backend utiliza **Django 5**, **Django REST Framework** e **Celery** para processar tarefas assíncronas de scraping.

## Iniciando

1. Instale as dependências em um ambiente virtual:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Execute as migrações do Django e crie um usuário administrador:
   ```bash
   cd backend/django_project
   python manage.py migrate
   python manage.py createsuperuser
   ```
3. Inicie o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```
4. Opcionalmente, suba todos os serviços com Docker:
   ```bash
   docker-compose up --build
   ```

A API ficará disponível em `http://localhost:8000/api/`.

## Estrutura

```
backend/
├── Dockerfile
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
```

Outras pastas importantes:

```
proxy/tor/      # container TOR para acesso .onion
scraper/        # adapters legados de scraping
worker/         # imagem do worker Celery
```

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

Os testes utilizam `pytest`. Após instalar as dependências, execute:

```bash
pytest -q
```

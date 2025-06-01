# Documentação do Backend - Plataforma de Threat Intelligence (Dark Web)

Este documento descreve a estrutura do backend da aplicação, com detalhes sobre a funcionalidade e responsabilidade de cada pasta e arquivo no projeto.

## Visão Geral

A aplicação é uma API construída em **FastAPI**, com integração ao **Celery** para tarefas assíncronas, **SQLAlchemy** como ORM, **Alembic** para migrações, e um sistema de scrapers para coleta de dados da dark web (TOR). O projeto também possui autenticação baseada em **JWT**.

---

## Estrutura de Pastas

```
.
├── Dockerfile
├── requirements.txt
└── app/
    ├── .env
    ├── alembic.ini
    ├── celery_app.py
    ├── init_db.py
    ├── main.py
    ├── __init__.py
    ├── api/
    ├── core/
    ├── db/
    ├── repository/
    ├── schemas/
    ├── scrapers/
    ├── services/
    ├── tasks/
    └── tests/
```

---

## Arquivos Raiz (app/)

### `.env`

Contém variáveis de ambiente como URL do banco, chave JWT, configurações do Celery, etc.

### `alembic.ini`

Arquivo de configuração do Alembic para realizar migrações no banco.

### `celery_app.py`

Inicializa a instância do Celery. Define o backend e o broker para processamento assíncrono de tarefas (ex: scraping).

### `init_db.py`

Script utilizado para criar as tabelas no banco com base nos modelos definidos.

### `main.py`

Ponto de entrada da aplicação FastAPI. Define o app, inclui middlewares, eventos e as rotas da API.

---

## `api/v1/`

Contém as rotas da API organizadas por versão e recurso.

### `deps.py`

Gerencia dependências injetadas nas rotas, como autenticação do usuário e sessões do banco.

### `routers/`

* `auth.py`: Rotas de login e autenticação via JWT.
* `leaks.py`: Endpoints para listar, buscar ou registrar vazamentos encontrados.
* `sites.py`: Gerenciamento dos sites monitorados.
* `snapshots.py`: Manipulação de snapshots de conteúdo capturado.

---

## `core/`

Lógica de configuração e segurança da aplicação.

### `config.py`

Carrega as configurações a partir do `.env` usando `pydantic.BaseSettings`.

### `jwt.py`

Funções para criação e verificação de tokens JWT.

### `logging_conf.py`

Configuração de logs estruturados para a aplicação.

### `security.py`

Funções auxiliares para hashing de senhas, geração de tokens, etc.

---

## `db/`

Gerencia a conexão e modelos do banco de dados.

### `session.py`

Criação da `SessionLocal` para comunicação com o banco via SQLAlchemy.

### `base.py`

Classe base declarativa utilizada por todos os modelos.

### `models/`

* `leak.py`: Modelo dos vazamentos detectados.
* `site.py`: Modelo dos sites monitorados.
* `snapshot.py`: Modelo de snapshot de conteúdo encontrado.
* `user.py`: Modelo dos usuários da plataforma.

---

## `repository/`

Implementa acesso direto ao banco, encapsulando as operações em classes ou funções reutilizáveis.

---

## `schemas/`

Define os modelos de entrada e saída da API usando **Pydantic**.

* `auth.py`: Schemas de login e tokens.
* `leak.py`: Estrutura dos dados de vazamento.
* `site.py`: Dados de entrada/saída dos sites monitorados.
* `task.py`: Status e retorno de tarefas assíncronas.

---

## `scrapers/`

Responsáveis por buscar dados em fontes específicas (ex: fóruns ou blogs na dark web).

* `base.py`: Classe base comum para scrapers.
* `akira_cli.py`: Scraper específico para o grupo de ransomware Akira.
* `ransomhouse.py`: Scraper do grupo RansomHouse.
* `init.py`: Scraper genérico para sites customizados.

---

## `services/`

Camada de regra de negócio que integra `repository`, `schemas`, e `scrapers`.

* `auth_service.py`: Funções para autenticação, registro e verificação de usuários.
* `scraper_service.py`: Orquestra scraping com Celery e salva os dados no banco.

---

## `tasks/`

Define as **tarefas assíncronas** que o Celery pode executar.

---

## `tests/`

Base para criação de testes automatizados.

---

## Tecnologias Utilizadas

* **FastAPI**: Framework web principal
* **Celery + Redis**: Fila para tarefas assíncronas
* **SQLAlchemy**: ORM
* **Alembic**: Migrações de banco
* **Docker**: Containerização
* **Pydantic**: Validação de dados
* **TOR**: Acesso à dark web

---
## Padrões de Código Utilizados
* **PEP8**: Guia oficial de estilo para Python.
* **Black**: Formatador automático de código para manter estilo consistente.
* **isort**: Para organizar os imports de forma padronizada.
* **Pylint / flake8**: Para linting e detecção de más práticas.
* **Clean Code**: Organização clara, sem duplicação de lógica, uso de nomes descritivos e responsabilidade única por módulo.
* **SOLID (aplicado onde aplicável)**: Separação de responsabilidades, dependências explícitas (ex: via deps.py), reutilização por meio de serviços e repositórios.

---

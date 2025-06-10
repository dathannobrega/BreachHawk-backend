# BreachHawk Docker Configuration

Este diretório contém as configurações Docker para o projeto BreachHawk, organizadas para permitir a execução em ambientes de produção e teste separadamente.

## Estrutura

```
docker/
├── docker-compose.base.yml    # Configurações base compartilhadas entre ambientes
├── docker-compose.yml         # Configuração para ambiente de produção
├── docker-compose.test.yml    # Configuração para ambiente de teste/desenvolvimento
└── environments/              # Variáveis de ambiente para diferentes ambientes
    ├── .env.production        # Variáveis para ambiente de produção
    └── .env.test              # Variáveis para ambiente de teste/desenvolvimento
```

## Ambientes Disponíveis

### Ambiente de Produção

Este ambiente é configurado para execução em servidores de produção com configurações otimizadas e seguras.

**Para iniciar o ambiente de produção:**

```bash
cd docker
docker-compose up -d
```

### Ambiente de Teste/Desenvolvimento

Este ambiente é configurado para desenvolvimento local e testes, incluindo o serviço de frontend e configurações mais adequadas para desenvolvimento.

**Para iniciar o ambiente de teste:**

```bash
cd docker
docker-compose -f docker-compose.test.yml up -d
```

## Serviços Disponíveis

Os seguintes serviços são configurados:

- **backend**: API Django do BreachHawk
- **db**: Banco de dados PostgreSQL
- **redis**: Cache Redis para tarefas assíncronas
- **mongo**: Banco de dados MongoDB
- **tor**: Proxy Tor para anonimidade nas operações
- **backend-worker**: Worker Celery para processamento de tarefas assíncronas
- **backend-beat**: Scheduler Celery para tarefas periódicas
- **frontend**: (apenas no ambiente de teste) Interface de usuário web

## Portas Expostas

- Backend: `8000` (http://localhost:8000)
- PostgreSQL: `5432` (postgresql://admin:password@localhost:5432)
- MongoDB: `27017` (mongodb://localhost:27017)
- Tor Proxy: `9050` (socks5://localhost:9050)
- Tor Control: `9051` (localhost:9051)
- Frontend (apenas ambiente de teste): `3000` (http://localhost:3000)

## Personalização dos Ambientes

Os arquivos de ambiente (`.env.production` e `.env.test`) na pasta `environments` podem ser modificados para configurar variáveis específicas para cada ambiente.

## Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Imagem `breachhawkfrontend:latest` disponível localmente (para ambiente de teste)

## Construindo a Imagem do Frontend

Para ambiente de teste, você precisa construir a imagem do frontend:

```bash
# Na pasta do projeto frontend
docker build -t breachhawkfrontend:latest .
```

## Volumes de Dados

- `pgdata`: Dados do PostgreSQL
- `mongodata`: Dados do MongoDB (produção)
- `mongodata_test`: Dados do MongoDB (teste)

Estes volumes são persistentes e mantêm os dados mesmo quando os contêineres são recriados.

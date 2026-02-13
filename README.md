# YpeTec

Plataforma de incubação e mentoria para projetos de empreendedorismo estudantil. O sistema gerencia todo o ciclo de vida dos projetos: submissão, avaliação, incubação, mentoria e vitrine pública.

## Tecnologias

- **Python 3.10+**
- **Django 5.x** - Framework web
- **Django REST Framework** - API REST
- **SimpleJWT** - Autenticação JWT
- **PostgreSQL** - Banco de dados (SQLite para desenvolvimento)
- **Pillow** - Processamento de imagens

## Requisitos

- Python 3.10 ou superior
- PostgreSQL (opcional para desenvolvimento)

## Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd ypetec
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=postgres://usuario:senha@localhost:5432/ypetec
JWT_SECRET_KEY=chave-jwt-para-tokens
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

> **Nota:** Para desenvolvimento, você pode omitir `DATABASE_URL` e o sistema usará SQLite automaticamente.

### 5. Execute as migrações

```bash
python manage.py migrate
```

### 6. Crie um superusuário

```bash
python manage.py createsuperuser
```

### 7. Inicie o servidor

```bash
python manage.py runserver
```

O servidor estará disponível em `http://localhost:8000`.

## Estrutura do Projeto

```
ypetec/
├── config/                 # Configurações Django
│   ├── settings/
│   │   ├── base.py        # Configurações base
│   │   ├── local.py       # Desenvolvimento
│   │   └── production.py  # Produção
│   └── urls.py            # Rotas principais
├── apps/
│   ├── core/              # Modelos base e utilitários
│   ├── contas/            # Usuários e autenticação
│   ├── editais/           # Editais (chamadas para submissão)
│   ├── projetos/          # Projetos e submissões
│   ├── avaliacoes/        # Avaliações de projetos
│   ├── mentorias/         # Solicitações de mentoria
│   ├── publicacoes/       # Vitrine pública
│   └── home/              # Página inicial
├── templates/             # Templates HTML
├── static/                # Arquivos estáticos
└── uploads/               # Uploads de usuários
```

## API

A API REST está disponível em `/api/`. Principais endpoints:

| Endpoint | Descrição |
|----------|-----------|
| `/api/auth/login` | Login (retorna tokens JWT) |
| `/api/auth/register` | Registro de novo usuário |
| `/api/auth/me` | Dados do usuário autenticado |
| `/api/users/` | Gerenciamento de usuários (admin) |
| `/api/calls/` | Editais |
| `/api/projects/` | Projetos |
| `/api/submissions/` | Submissões |
| `/api/evaluations/` | Avaliações |
| `/api/mentorship-requests/` | Solicitações de mentoria |
| `/api/publications/` | Publicações (vitrine) |

### Autenticação

A API usa autenticação JWT. Após o login, inclua o token no header:

```
Authorization: Bearer <access_token>
```

## Papéis de Usuário

| Papel | Descrição |
|-------|-----------|
| **ADMIN** | Gerencia editais, avalia projetos, publica na vitrine |
| **ALUNO** | Cria projetos, submete a editais, solicita mentoria |
| **MENTOR** | Fornece mentoria aos projetos incubados |
| **INVESTIDOR** | Visualiza oportunidades de investimento |

## Ciclo de Vida do Projeto

```
PRE_SUBMISSAO → SUBMETIDO → APROVADO → INCUBADO
                    ↓
               REPROVADO
                    ↓
                AJUSTES (pode resubmeter)
```

## Comandos Úteis

```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Shell interativo
python manage.py shell

# Coletar arquivos estáticos (produção)
python manage.py collectstatic
```

## Produção

Para rodar em produção:

1. Configure `DJANGO_SETTINGS_MODULE=config.settings.production`
2. Defina `DEBUG=False` e uma `SECRET_KEY` segura
3. Configure o banco PostgreSQL via `DATABASE_URL`
4. Use Gunicorn como servidor WSGI:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```


## Deploy na Railway (segredos em runtime)

Para evitar alertas de segurança e garantir que os segredos não sejam usados em build-time:

1. Em **Railway → Service → Variables**, cadastre como variáveis de **runtime**:
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `RESEND_API_KEY`
   - (e demais segredos, como `DATABASE_URL`)
2. Não use segredos em **build args**.
3. Não use `ARG`/`ENV` de build para segredos em Dockerfile/Nixpacks customizado.
4. Faça redeploy do serviço após atualizar as variáveis.

Nesta base, o deploy foi ajustado para executar `collectstatic` e `migrate` no **start/runtime** (`start.sh`), evitando dependência de segredos no build.

## Licença

Este projeto é proprietário e de uso restrito.

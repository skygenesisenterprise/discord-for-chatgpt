# Discord for ChatGPT

[![License: Apache 2.0](https://img.shields.io/github/license/skygenesisenterprise/discord-for-chatgpt)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-1.1-000000)](https://modelcontextprotocol.io)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](.github/CONTRIBUTING.md)
[![Discord](https://img.shields.io/badge/Discord-join-5865F2?logo=discord&logoColor=white)](https://discord.gg/GUkDugVh34)

<div align="center">
  </br>
</div>

> Let ChatGPT understand, structure, and safely manage your Discord servers.

**Discord for ChatGPT** is an open-source, self-hostable application that connects ChatGPT to Discord through the Model Context Protocol (MCP). It allows ChatGPT to discover server structure, read messages, prepare and execute changes with controlled approval flows, and manage moderation, webhooks, and more - all through Discord's official API with strict permission checks.

**Perfect for:** server administrators who want AI-assisted server management, communities looking for safer automation, and teams who want auditable Discord operations through natural language.

## Contents

- [Discord for ChatGPT](#discord-for-chatgpt)
  - [Contents](#contents)
  - [Why Discord for ChatGPT matters](#why-discord-for-chatgpt-matters)
  - [What you can do](#what-you-can-do)
    - [Discover \& Read](#discover--read)
    - [Structure \& Roles](#structure--roles)
    - [Messages \& Community](#messages--community)
    - [Webhooks \& Integrations](#webhooks--integrations)
    - [Moderation \& Audit](#moderation--audit)
  - [Quick start](#quick-start)
    - [Self-host with Docker Compose](#self-host-with-docker-compose)
  - [Architecture](#architecture)
  - [How it's built](#how-its-built)
    - [Project layout](#project-layout)
    - [Core components](#core-components)
    - [Tech stack](#tech-stack)
  - [Development](#development)
    - [Requirements](#requirements)
    - [Setup](#setup)
    - [Commands](#commands)
  - [Security](#security)
  - [Contributing](#contributing)
  - [License](#license)
  - [Note](#note)

## Why Discord for ChatGPT matters

🎯 **Official API only** — No self-bots or user automation. Everything uses Discord's official OAuth2 and bot APIs with proper authentication.

🔒 **Secure by design** — Operations are validated, require explicit approval for mutations, and follow the principle of least privilege with full audit trails.

👁️ **Transparent operations** — Before any change, ChatGPT presents an interactive preview with diffs, risks, and required permissions for your review and confirmation.

🧩 **MCP-first integration** — Built as a ChatGPT App via Model Context Protocol with typed tools, proper error handling, and session-based authorization.

🤝 **Auditable & controlled** — Every mutation is tracked through operation plans, single-use approvals, post-execution verification, and comprehensive logging.

## What you can do

### Discover & Read

- **Identity** - Connect and identify your Discord account via OAuth2
- **Server overview** - List accessible servers and their capabilities
- **Structure mapping** - Inventory categories, channels, roles, and permissions
- **Message exploration** - Read and search messages in accessible channels with pagination
- **Audit reports** - Generate reports on naming, categories, and permission consistency

### Structure & Roles

- **Channel management** - Create, rename, update, and reorganize channels
- **Category management** - Create, modify, and structure channel categories
- **Role management** - Create, update roles and manage permissions within authorized scopes
- **Safe reorganization** - Plan and preview structural changes before execution

### Messages & Community

- **Message preparation** - Draft messages with previews before sending
- **Announcements** - Post in announcement-compatible channels
- **Message management** - Edit or delete messages when permissions allow
- **Thread access** - Read accessible threads and conversations

### Webhooks & Integrations

- **Webhook inventory** - List webhooks with metadata only (tokens never exposed)
- **Webhook management** - Create, update, or revoke webhooks when authorized
- **Secure handling** - Webhook URLs and tokens are treated as secrets and never logged

### Moderation & Audit

- **Member inspection** - View accessible member information
- **Moderation actions** - Prepare and execute kicks/bans with proper authorization
- **Audit trail** - Track all operations, approvals, and results
- **Permission validation** - Real-time permission checks before every action

## Quick start

### Self-host with Docker Compose

Requirements: Docker Engine with the Compose plugin. You'll need a Discord application for OAuth2 and optionally a bot for extended permissions.

```bash
git clone https://github.com/skygenesisenterprise/discord-for-chatgpt.git
cd discord-for-chatgpt
cp .env.example .env
```

Edit `.env` with your Discord application credentials. Generate secure values for `SECRET_KEY` and `ENCRYPTION_KEY`:

```bash
openssl rand -hex 32  # for SECRET_KEY
openssl rand -base64 32  # for ENCRYPTION_KEY
```

Start the stack:

```bash
docker compose up --build -d
docker compose logs -f app
```

The API will be available at [http://localhost:8000](http://localhost:8000). Configure your Discord OAuth2 redirect URI to point to `http://localhost:8000/oauth/discord/callback`.

For production, use HTTPS, proper secrets management, and follow the [deployment guide](docs/deployment.md).

## Architecture

Discord for ChatGPT follows a layered architecture with clear separation of concerns:

1. **ChatGPT App** - Interacts with users, displays previews, and requests confirmations
2. **MCP Gateway** - Exposes typed tools via Streamable HTTP with validation and auth
3. **Identity & Authorization** - OAuth2 flow, session management, token encryption
4. **Policy & Approval Engine** - Risk assessment, operation planning, single-use approvals
5. **Discord API Adapter** - Centralized API calls with rate limiting and error handling
6. **Persistence & Audit** - PostgreSQL for operations, approvals, and audit logs

All mutations flow through: prepare → plan → review → approve → validate → execute → verify → audit.

## How it's built

### Project layout

```text
discord-for-chatgpt/
├── src/discord_for_chatgpt/  # Application source code
│   ├── api/                 # REST endpoints (health, oauth, approvals)
│   ├── mcp/                 # MCP server, auth, schemas, errors
│   ├── identity/            # OAuth2, sessions, token storage
│   ├── discord/             # Discord API client and resource handlers
│   ├── services/            # Business logic (discovery, planning, execution)
│   ├── policies/            # Risk assessment and validation
│   ├── db/                  # Models, repositories, migrations
│   └── ui/                  # UI resources and templates
├── tests/                   # Unit, integration, security, contract, e2e tests
├── docs/                    # Architecture, OAuth, permissions, security docs
├── pyproject.toml           # Dependencies and project config
├── Dockerfile               # Container definition
├── compose.yaml             # Local development stack
└── alembic.ini              # Database migrations
```

### Core components

| Module | Role |
| --- | --- |
| `mcp/` | MCP server implementation with typed tools and authentication |
| `api/` | HTTP endpoints for OAuth callbacks and approval confirmations |
| `identity/` | Discord OAuth2 flow, session management, encrypted token storage |
| `discord/` | Official Discord API client with rate limiting and normalization |
| `services/` | Application services for discovery, planning, execution, and auditing |
| `policies/` | Risk classification, permission validation, and safety checks |
| `db/` | Data persistence with PostgreSQL and Alembic migrations |

### Tech stack

| Domain | Technology |
| --- | --- |
| Runtime | Python 3.12+ |
| API Framework | FastAPI, Starlette |
| MCP | Official Python MCP SDK |
| Validation | Pydantic v2 |
| HTTP Client | httpx |
| Database | PostgreSQL with SQLAlchemy 2, Alembic |
| Security | Cryptography for token encryption |
| Observability | OpenTelemetry, structured logging |
| Testing | pytest, pytest-asyncio, respx |

## Development

### Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) for dependency management
- PostgreSQL 16 (or use Docker Compose)
- Discord Application credentials

### Setup

```bash
git clone https://github.com/skygenesisenterprise/discord-for-chatgpt.git
cd discord-for-chatgpt
cp .env.example .env
# Edit .env with your credentials
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Commands

| Command | Purpose |
| --- | --- |
| `uvicorn discord_for_chatgpt.main:app --reload` | Start development server |
| `pytest` | Run test suite |
| `ruff check .` | Run linting |
| `ruff format .` | Format code |
| `mypy src/` | Type checking |
| `alembic upgrade head` | Run database migrations |
| `alembic revision --autogenerate -m "message"` | Create new migration |

## Security

Security is a core design principle. Key measures include:

- **No self-bots** - Only official Discord APIs
- **Least privilege** - Minimal scopes and permission checks
- **Approval required** - All mutations need explicit, single-use approval
- **Secret protection** - Tokens encrypted at rest, never logged
- **Prompt injection defense** - Discord content treated as untrusted data
- **Audit logging** - Complete trail of operations and approvals
- **Rate limiting** - Respects Discord API limits

Do not report security vulnerabilities in public issues. Follow the private reporting instructions in [SECURITY.md](SECURITY.md).

## Contributing

Contributions are welcome! Please read the [Code of Conduct](CODE_OF_CONDUCT.md) before participating, then follow the guidelines in [CONTRIBUTING.md](.github/CONTRIBUTING.md).

- Follow the existing code style and conventions
- Write tests for new functionality
- Update documentation as needed
- Use [Conventional Commits](https://www.conventionalcommits.org) for commit messages
- Ensure all tests pass and linting is clean before submitting PRs

## License

This project is licensed under the [MIT License](LICENSE).

## Note

Discord for ChatGPT is an independent open-source project. It is not affiliated with, endorsed by, or sponsored by Discord Inc. or OpenAI. Use of Discord's API is subject to Discord's [Terms of Service](https://discord.com/terms) and [Developer Terms](https://discord.com/developers/docs/legal).

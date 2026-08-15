# Enterprise Telegram Agent

Production-ready Telegram bot with LangChain agents, async FastAPI, and PostgreSQL.

## Architecture

Telegram -> FastAPI Webhook -> LangChain Agent -> PostgreSQL


## Quick Start

### Clone & setup

```bash
git clone https://github.com/YevheniiaVovk/enterprise-telegram-agent.git
cd enterprise-telegram-agent
```

### Activate venv (Windows)

```bash
.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
uv sync
```

### Run with Docker

```bash
docker-compose up --build
```

## Project Structure

src/
├── agent/ # LangChain agent core
├── telegram/ # Telegram webhook handlers
├── database/ # SQLAlchemy models & checkpointer
└── config.py # Pydantic settings


## Technologies

- **FastAPI** - async web framework
- **LangChain** - AI agents & tools
- **SQLAlchemy** - ORM for PostgreSQL
- **asyncpg** - async PostgreSQL driver
- **Telegram Bot API** - webhook-based bot

## Development

```bash
# Install dev dependencies
uv sync --all-groups

# Run tests
pytest

# Format code
black src/
ruff check src/
```

## License

MIT
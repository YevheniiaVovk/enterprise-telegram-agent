@"
# Enterprise Telegram Agent

Production-ready Telegram bot with LangChain agents, async FastAPI, and PostgreSQL.

## Architecture

\`\`\`
Telegram → FastAPI Webhook → LangChain Agent → PostgreSQL
\`\`\`

## Quick Start

\`\`\`bash
# Clone & setup
git clone https://github.com/YevheniiaVovk/enterprise-telegram-agent.git
cd enterprise-telegram-agent

# Activate venv (Windows)
.venv\Scripts\activate

# Install dependencies
uv sync

# Run with Docker
docker-compose up
\`\`\`

## Project Structure

\`\`\`
src/
├── agent/       # LangChain agent core
├── telegram/    # Telegram webhook handlers
├── database/    # SQLAlchemy models & checkpointer
└── config.py    # Pydantic settings
\`\`\`
"@ | Out-File -Encoding UTF8 README.md
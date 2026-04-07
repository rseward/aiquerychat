# aiquerychat

LLM-guided SQL query tool with a Textual TUI chat interface. Ask your database questions in plain English — the LLM translates them to SELECT queries, executes them, and displays results as formatted tables. Supports exporting results to pipe-delimited files.

## Features

- **Natural language to SQL**: Ask questions in plain English; the LLM generates and runs SELECT queries against your database.
- **Interactive TUI chat**: Textual-based terminal UI with chat bubbles, syntax-highlighted result tables, and inline error recovery.
- **Clarifying对话**: The LLM may ask follow-up questions when a request is vague.
- **Query auto-fix**: When a generated SQL query fails, the LLM attempts to correct it automatically (up to 5 retries).
- **Pipe-delimited export**: Export any result set to a `.txt` file with `|` as the field delimiter.
- **Schema context**: Provide a schema file (`--schema`) so the LLM understands your table structure.
- **Multi-backend LLM**: Works with Ollama or any OpenAI-compatible API endpoint.
- **TUI commands**:
  - `/new` — start a fresh conversation, clear chat history and query state.
  - `Ctrl+C` / `Ctrl+Q` — quit.

## Supported Databases

Currently tested with Microsoft SQL Server (MSSQL) via `pymssql`. The SQLAlchemy engine is pluggable, so other databases supported by SQLAlchemy (PostgreSQL, MySQL, SQLite, etc.) may work with minimal changes.

## Architecture

```
aiquerychat/
├── src/aiquerychat/
│   ├── __init__.py       # Package init
│   ├── __main__.py       # python -m aiquerychat entry point
│   ├── cli.py            # Click CLI — parses args, loads .env, launches TUI
│   ├── db.py             # SQLAlchemy Database wrapper (execute, close)
│   ├── export.py         # Pipe-delimited CSV export + filename suggestion
│   ├── llm.py            # any-llm-sdk LLM wrapper (complete, complete_streaming)
│   ├── schema.py         # Schema file loader
│   └── tui.py            # Textual TUI — chat UI, query execution, export workflow
├── tests/                # pytest test suite
├── pyproject.toml        # Project config, dependencies
├── Makefile              # venv, deps, test, lint, run targets
├── .env.example          # Environment variable template
├── PROMPT.md             # Original project brief/prompt
├── TODO.md               # Planned enhancements
└── schemaContMgmtApp.md  # Example schema for the landlord/ContMgmt database
```

### Key Dependencies

| Package | Purpose |
|---|---|
| `textual` | Terminal UI framework |
| `sqlalchemy` | Database ORM and query engine |
| `pymssql` | MSSQL driver |
| `any-llm-sdk` | LLM API client (OpenAI-compatible) |
| `click` | CLI argument parsing |
| `python-dotenv` | `.env` file loading |
| `rich` | Table formatting in TUI |
| `ollama` | Ollama Python client (installed with any-llm-sdk) |

## Installation

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (package manager)
- An LLM backend (Ollama recommended for local use)
- A SQL database accessible from your network

### 1. Clone and set up virtual environment

```bash
git clone <repository-url>
cd aiquerychat
make venv
make deps
```

Or manually:

```bash
uv venv
uv sync
uv pip install --python .venv/bin/python -e .
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# SQLAlchemy database URL
DATABASE_URL=mssql+pymssql://user:password@host/database

# LLM API — Ollama local default
OPENAI_BASE_URL=http://127.0.0.1:11434/api/chat/v1
OPENAI_TOKEN=not-needed        # Required by SDK, use any value for Ollama

# Default model
MODEL=gemma3:latest
```

For **Ollama**, install and start it:

```bash
# Install Ollama (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Pull the default model
ollama pull gemma3:latest

# Start Ollama server (runs on port 11434 by default)
ollama serve
```

### 3. (Optional) Provide a schema file

Point to your database schema with `--schema`. The project ships with `schemaContMgmtApp.md` as an example for the landlord/ContMgmtApp database. Replace or update this file to match your actual database structure.

## Usage

### Start the TUI

```bash
make run
```

Or directly:

```bash
uv run python -m aiquerychat
```

With custom options:

```bash
python -m aiquerychat \
  --schema ./my_schema.md \
  --url "mssql+pymssql://user:pass@host/db" \
  --llmurl http://127.0.0.1:11434/api/chat/v1 \
  --model gemma3:latest
```

### Chat Interface

- Type your question in plain English and press **Enter**.
- The assistant may ask clarifying questions before generating a query.
- Once a `SELECT` is ready, it is executed automatically and results display as a formatted table.
- Type `/new` to start a fresh conversation.

### Exporting Results

After viewing results, the LLM may offer to export. You can also trigger export by asking "export this". The app writes a pipe-delimited `.txt` file.

### Quit

```
Ctrl+C   or   Ctrl+Q
```

## Makefile Targets

| Target | Command | Description |
|---|---|---|
| `venv` | `make venv` | Create virtual environment with uv |
| `deps` | `make deps` | Install sync dependencies and install package |
| `test` | `make test` | Run pytest test suite |
| `lint` | `make lint` | Run ruff lint checks on `src/` |
| `run` | `make run` | Start the TUI chat session |

## Configuration Reference

| Environment Variable | CLI Option | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | `--url` / `-u` | *(required)* | SQLAlchemy connection URL |
| `OPENAI_BASE_URL` | `--llmurl` / `-l` | `http://127.0.0.1:11434/api/chat/v1` | LLM API base URL |
| `OPENAI_TOKEN` | — | `not-needed` | API token (any value for Ollama) |
| `MODEL` | `--model` / `-m` | `gemma3:latest` | LLM model name |
| `LLM_PROVIDER` | `--provider` / `-p` | `ollama` | LLM provider (`ollama` or `openai`) |
| *(schema file)* | `--schema` / `-s` | `schemaContMgmtApp.md` | Path to database schema markdown |

## Testing

```bash
make test
```

Tests are in `tests/` and cover:
- `test_async.py` — async LLM and DB operations
- `test_db.py` — database query execution
- `test_export.py` — pipe-delimited export
- `test_llm.py` — LLM completion logic
- `test_schema.py` — schema file loading
- `test_tui.py` — TUI component rendering

Run linting separately:

```bash
make lint
```

## Known Limitations

- Only `SELECT` queries are executed. `INSERT`, `UPDATE`, `DELETE`, and DDL are blocked by the LLM prompt instructions.
- SQL query auto-fix retries up to 5 times before giving up.
- Tested primarily with MSSQL. Other databases may need adapter work for schema-specific SQL syntax.
- The LLM must be an OpenAI-compatible chat completions endpoint. Native Ollama via `ollama` Python library is used automatically when provider is `ollama`.

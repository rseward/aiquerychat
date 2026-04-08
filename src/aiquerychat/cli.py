"""CLI entry point using click."""

from __future__ import annotations

import os
from pathlib import Path

import click
from dotenv import load_dotenv

from aiquerychat.tui import AiQueryChatApp


def resolve_path(ctx: click.Context, param: click.Parameter, value: str | None) -> str | None:
    """Expand ~ and relative paths."""
    if value is None:
        return value
    return str(Path(value).expanduser().resolve())


@click.command()
@click.option(
    "--schema",
    "-s",
    default="schemaContMgmtApp.md",
    show_default=True,
    help="Path to schema file",
    callback=resolve_path,
)
@click.option(
    "--url",
    "-u",
    default=None,
    help="SQLAlchemy database URL (overrides .env)",
)
@click.option(
    "--llmurl",
    "-l",
    default=None,
    help="LLM API base URL (overrides .env)",
)
@click.option(
    "--provider",
    "-p",
    default=None,
    help="LLM provider, e.g. ollama or openai (overrides .env)",
)
def run(schema: str | None, url: str | None, llmurl: str | None, provider: str | None) -> None:
    """Start the AI Query Tool TUI session."""
    # Load .env file
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()  # Try .env in current dir

    # Get values from env or CLI args
    db_url = url or os.getenv("DATABASE_URL")
    llm_url = llmurl or os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:11434")
    llm_token = os.getenv("OPENAI_TOKEN", "not-needed")
    llm_model = os.getenv("MODEL", "gemma3:latest")
    llm_provider = provider or os.getenv("LLM_PROVIDER", "ollama")

    if not db_url:
        raise click.ClickException(
            "DATABASE_URL not set. Provide --url or set DATABASE_URL in .env"
        )

    if not Path(schema).exists():
        raise click.ClickException(f"Schema file not found: {schema}")

    app = AiQueryChatApp(
        db_url=db_url,
        llm_url=llm_url,
        llm_token=llm_token,
        llm_model=llm_model,
        schema_path=schema,
        llm_provider=llm_provider,
    )
    app.run()


if __name__ == "__main__":
    run()

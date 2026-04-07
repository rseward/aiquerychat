"""Database connection using SQLAlchemy."""

from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


class Database:
    """SQLAlchemy database connection wrapper."""

    def __init__(self, url: str):
        self.url = url
        self._engine: Engine | None = None

    @property
    def engine(self) -> Engine:
        """Lazy engine creation."""
        if self._engine is None:
            self._engine = create_engine(self.url)
        return self._engine

    def execute(self, query: str) -> list[dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts."""
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            rows = [dict(row._mapping) for row in result]
        return rows

    def close(self) -> None:
        """Dispose the engine."""
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None

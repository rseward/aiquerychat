"""Schema loading utilities."""

from __future__ import annotations

from pathlib import Path


def load_schema(schema_path: str | Path) -> str:
    """Load and return schema file contents."""
    path = Path(schema_path)
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    return path.read_text(encoding="utf-8")

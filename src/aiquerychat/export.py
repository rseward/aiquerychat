"""Pipe-delimited export utilities."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def export_pipe_delimited(
    data: list[dict[str, Any]],
    output_path: str | Path,
) -> None:
    """Write query results to a pipe-delimited file."""
    if not data:
        raise ValueError("No data to export")

    path = Path(output_path)
    fieldnames = list(data[0].keys())

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        writer.writeheader()
        writer.writerows(data)


def suggest_filename(user_text: str | None = None) -> str:
    """Suggest a filename for export based on user input."""
    if user_text:
        # Extract key words, lowercase, replace spaces with underscores
        slug = "".join(c if c.isalnum() else "_" for c in user_text.lower())
        slug = "_".join(w for w in slug.split("_") if w)[:40]
        return f"query_{slug}.txt"
    return "query_results.txt"

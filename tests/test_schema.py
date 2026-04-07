"""Tests for schema.py."""

import pytest

from aiquerychat.schema import load_schema


def test_load_schema_reads_file(tmp_path):
    schema_file = tmp_path / "schema.md"
    schema_file.write_text("# Schema\n\nTable: users\n")
    result = load_schema(schema_file)
    assert result == "# Schema\n\nTable: users\n"


def test_load_schema_raises_on_missing():
    with pytest.raises(FileNotFoundError):
        load_schema("/nonexistent/schema.md")

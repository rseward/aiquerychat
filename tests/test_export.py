"""Tests for export.py."""

import os
import tempfile

import pytest

from aiquerychat.export import export_pipe_delimited, suggest_filename


class TestExportPipeDelimited:
    def test_exports_basic_data(self):
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        with tempfile.NamedTemporaryFile(mode="r", delete=False, suffix=".txt") as f:
            path = f.name
        try:
            export_pipe_delimited(data, path)
            with open(path) as f:
                content = f.read()
            lines = content.strip().split("\n")
            assert lines[0] == "name|age"
            assert "Alice|30" in content
            assert "Bob|25" in content
        finally:
            os.unlink(path)

    def test_raises_on_empty_data(self):
        with pytest.raises(ValueError, match="No data to export"):
            export_pipe_delimited([], "out.txt")


class TestSuggestFilename:
    def test_basic_suggestion(self):
        name = suggest_filename("list all users")
        assert name.startswith("query_")
        assert name.endswith(".txt")
        assert "list_all_users" in name

    def test_no_text(self):
        name = suggest_filename()
        assert name == "query_results.txt"

    def test_truncates_long_input(self):
        long_text = "a" * 100
        name = suggest_filename(long_text)
        assert len(name) <= 50  # slug + prefix + suffix

"""Tests for db.py."""

from unittest.mock import MagicMock, patch

import pytest

from aiquerychat.db import Database


class TestDatabase:
    @pytest.fixture
    def db(self):
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        with patch("aiquerychat.db.create_engine", return_value=mock_engine):
            db_instance = Database("mssql+pymssql://user:pass@host/db")
            # Trigger lazy engine creation while patch is active
            _ = db_instance.engine

        # Patch stays active via mockEngine stored on the instance
        yield db_instance, mock_conn, mock_engine

    def test_execute_returns_list_of_dicts(self, db):
        db_instance, mock_conn, _ = db
        mock_row = MagicMock()
        mock_row._mapping = {"name": "Alice", "age": 30}
        mock_conn.execute.return_value = [mock_row]

        result = db_instance.execute("SELECT name, age FROM users")
        assert result == [{"name": "Alice", "age": 30}]

    def test_execute_close(self, db):
        db_instance, _, mock_engine = db
        db_instance.close()
        mock_engine.dispose.assert_called_once()

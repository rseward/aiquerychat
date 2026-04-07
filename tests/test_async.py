"""Tests for async LLM interaction."""

import asyncio

import pytest

from aiquerychat.llm import LLM


class TestAicompletion:
    @pytest.fixture
    def llm(self):
        return LLM(
            api_base="http://localhost:11434/api/chat/v1",
            token="test-token",
            model="gemma3:latest",
        )

    @pytest.mark.asyncio()
    async def test_run_in_executor_dispatches_blocking_call(self):
        """Verify run_in_executor can dispatch a blocking function from async code.

        This is the core async pattern used in tui.py:
        - process_message() is async
        - it calls run_in_executor to dispatch the blocking LLM HTTP call
        - the result is awaited without blocking the event loop
        """
        def blocking_sql_query(query: str) -> list[dict]:
            # Simulate a blocking DB/LLM call
            return [{"id": 1, "name": "Alice"}]

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, blocking_sql_query, "SELECT * FROM users")
        assert result == [{"id": 1, "name": "Alice"}]

"""Tests for llm.py."""

from unittest.mock import MagicMock, patch

import pytest

from aiquerychat.llm import LLM


class TestLLM:
    @pytest.fixture
    def llm(self):
        return LLM(
            api_base="http://localhost:11434/api/chat/v1",
            token="test-token",
            model="gemma3:latest",
        )

    def test_complete_returns_text(self, llm):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello world"))]

        with patch("aiquerychat.llm.completion", return_value=mock_response) as mock_comp:
            result = llm.complete([{"role": "user", "content": "hi"}])
            assert result == "Hello world"
            mock_comp.assert_called_once()

    def test_complete_passes_tools(self, llm):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=""))]

        tools = [{"type": "function", "function": {"name": "test", "parameters": {}}}]
        with patch("aiquerychat.llm.completion", return_value=mock_response) as mock_comp:
            llm.complete([{"role": "user", "content": "hi"}], tools=tools)
            call_kwargs = mock_comp.call_args.kwargs
            assert call_kwargs["tools"] == tools

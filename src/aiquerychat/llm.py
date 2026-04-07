"""LLM connection using any-llm-sdk."""

from __future__ import annotations

from typing import Any

from any_llm import completion


class LLM:
    """Wrapper around any-llm-sdk for OpenAI-compatible endpoints."""

    def __init__(self, api_base: str, token: str, model: str):
        self.api_base = api_base
        self.token = token
        self.model = model

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        """Send a completion request and return the assistant's text response."""
        response = completion(
            model=self.model,
            messages=messages,
            provider="openai",
            api_key=self.token,
            api_base=self.api_base,
            tools=tools,
        )
        return response.choices[0].message.content or ""

    def complete_streaming(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ):
        """Streaming completion yielding text chunks."""
        response = completion(
            model=self.model,
            messages=messages,
            provider="openai",
            api_key=self.token,
            api_base=self.api_base,
            tools=tools,
            stream=True,
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

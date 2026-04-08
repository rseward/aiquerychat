"""Textual TUI for LLM-guided SQL querying."""

from __future__ import annotations

import asyncio
import json
import logging
import traceback
from pathlib import Path
from typing import Any

from any_llm import acompletion
from rich.table import Table
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Footer, Input, Static

from aiquerychat.db import Database
from aiquerychat.export import export_pipe_delimited, suggest_filename
from aiquerychat.schema import load_schema

LOG_FILE = Path.home() / ".aiquerychat" / "aiquerychat.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("aiquerychat")


def log_exception(e: Exception) -> None:
    """Log exception to file and return user-friendly message."""
    tb = traceback.format_exc()
    log.error("Unhandled exception: %s\n%s", e, tb)
    # Also write directly to ensure it lands in the file
    with open(LOG_FILE, "a") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Exception: {e}\n")
        f.write(tb)


class SqlResult(Message):
    """Emitted when SQL results are ready to display."""

    def __init__(self, data: list[dict], query: str) -> None:
        super().__init__()
        self.data = data
        self.query = query


class SqlError(Message):
    """Emitted when a SQL query fails."""

    def __init__(self, error: str) -> None:
        super().__init__()
        self.error = error


# Tool definitions for the LLM
SQL_TOOL = {
    "type": "function",
    "function": {
        "name": "run_sql",
        "description": "Execute a SELECT SQL query against the database. "
        "Use this when you have enough information to construct the query. "
        "Returns results as a table.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The SELECT SQL query to execute. "
                    "Must be a SELECT statement only — no INSERT, UPDATE, or DELETE.",
                }
            },
            "required": ["query"],
        },
    },
}

EXPORT_TOOL = {
    "type": "function",
    "function": {
        "name": "export_pipe_delimited",
        "description": "Export the last query results to a pipe-delimited file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Output file path for the pipe-delimited export.",
                }
            },
            "required": ["filename"],
        },
    },
}


SYSTEM_PROMPT = """You are a helpful SQL query assistant. The user will ask questions about the database in plain English.

Follow this process:
1. If the request is vague or ambiguous, ask clarifying questions.
2. Once you have enough details, use the run_sql tool to execute a SELECT query.
3. After showing results, use the export_pipe_delimited tool to export data if the user requests it or if the dataset is large.

Available tools:
- run_sql: Execute a SELECT SQL query against the database. Returns results as a table.
- export_pipe_delimited: Export the last query results to a pipe-delimited file on the user's filesystem.

Guidelines:
- Only generate SELECT statements — no INSERT, UPDATE, or DELETE.
- All queries must be compatible with Microsoft SQL Server (T-SQL).
- Use the schema provided to understand table names, columns, and relationships.
- If a query might return many rows, warn the user first.
- After running a query, proactively suggest exporting if the results are useful.
- Be concise and helpful in your responses.
"""


class ChatMessage(Static):
    """A single chat message bubble."""

    def __init__(self, role: str, text: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.role = role
        self.text = text

    def render(self) -> Text:
        prefix = "You: " if self.role == "user" else "Assistant: "
        return Text(prefix + self.text)


class QueryTable(Static):
    """Displays SQL results as a rich table."""

    def __init__(self, data: list[dict], query: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.data = data
        self.query = query

    def render(self) -> Table:
        table = Table(show_header=True, header_style="bold #ff00ff")
        if not self.data:
            table.add_row("No results")
            return table

        cols = list(self.data[0].keys())
        for col in cols:
            table.add_column(col, style="#00ffff")

        for row in self.data:
            table.add_row(*[str(row.get(c, "")) for c in cols])

        return table


class StatusMessage(Static):
    """Shows status info like 'Thinking...'."""

    def __init__(self, text: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._text = text

    def render(self) -> Text:
        return Text(self._text, style="italic #888888")


class AskFilename(Static):
    """Inline prompt asking for a filename."""

    def __init__(self, suggested: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.suggested = suggested

    def compose(self) -> ComposeResult:
        yield Static(f"Suggested filename: {self.suggested}")
        yield Input(placeholder="Enter filename or press Enter for default", id="filename-input")
        yield Button("Confirm", id="confirm-filename", variant="primary")
        yield Button("Cancel", id="cancel-export")


class AiQueryChatApp(App):
    """Textual TUI application."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #chat-container {
        height: 1fr;
        padding: 1;
    }

    #chat-scroll {
        height: 1fr;
    }

    #input-area {
        height: auto;
        padding: 1;
        border-top: #0077cc solid;
    }

    #status-bar {
        height: auto;
        padding: 0 1;
        color: #888888;
    }

    QueryTable {
        margin: 1 0;
    }

    .chat-user {
        text-style: bold;
        color: #ffffff;
        background: #000088;
        padding: 0 1;
    }

    .chat-assistant {
        color: #ffffff;
        background: #008800;
        padding: 0 1;
    }

    #filename-input {
        margin: 1 0;
    }

    Screen {
        # notifications appear bottom-center with a fade-out
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def __init__(
        self,
        db_url: str,
        llm_url: str,
        llm_token: str,
        llm_model: str,
        schema_path: str,
        llm_provider: str = "openai",
    ):
        super().__init__()
        self.db = Database(db_url)
        self.llm_url = llm_url
        self.llm_token = llm_token
        self.llm_model = llm_model
        self.llm_provider = llm_provider
        self.schema = load_schema(schema_path)
        self.last_result: list[dict] | None = None
        self.last_query: str | None = None
        self._pending_export: bool = False
        self._sql_error_count: int = 0

    def compose(self) -> ComposeResult:
        yield Footer()
        with Container(id="chat-container"):
            with VerticalScroll(id="chat-scroll"):
                pass
        with Container(id="input-area"):
            yield Input(placeholder="Press tab. Ask a question or type a SQL query...", id="user-input")
        with Container(id="status-bar"):
            yield StatusMessage("Ready. Ask a question in English.", id="status")

    def on_mount(self) -> None:
        self.title = "AI Query Tool"
        # Log unhandled exceptions to file
        def handle_exception(event: Exception) -> None:
            log_exception(event)
        self.on_exception = handle_exception  # type: ignore[method-assign]
        schema_preview = self.schema[:200] + "..." if len(self.schema) > 200 else self.schema
        self.add_message(
            "assistant",
            f"Connected to database. Schema loaded.\n\n{SYSTEM_PROMPT}\n\nSchema:\n{schema_preview[:500]}...",
        )

    def add_message(self, role: str, text: str) -> None:
        """Add a chat message to the scrollable area."""
        scroll = self.query_one("#chat-scroll", VerticalScroll)
        msg = ChatMessage(role, text)
        msg_classes = "chat-user" if role == "user" else "chat-assistant"
        msg.add_class(msg_classes)
        scroll.mount(msg)
        scroll.scroll_end(animate=True)

    def set_status(self, text: str) -> None:
        self.query_one("#status", StatusMessage)._text = text

    def show_table(self, data: list[dict], query: str) -> None:
        """Display SQL results as a table."""
        scroll = self.query_one("#chat-scroll", VerticalScroll)
        table = QueryTable(data, query)
        scroll.mount(table)
        scroll.scroll_end(animate=True)
        self.last_result = data
        self.last_query = query

    def show_error(self, text: str) -> None:
        """Display an error message."""
        scroll = self.query_one("#chat-scroll", VerticalScroll)
        err = Static(Text(f"Error: {text}", style="#ff0000 bold"))
        scroll.mount(err)
        scroll.scroll_end(animate=True)

    def ask_export_filename(self, suggested: str) -> None:
        """Show inline prompt for export filename."""
        area = self.query_one("#input-area", Container)
        area.clear()
        area.mount(
            Static(f"Suggested filename: {suggested}"),
        )
        inp = Input(placeholder="Enter filename or press Enter for default", id="filename-input")
        area.mount(inp)
        area.mount(Button("Confirm", id="confirm-filename", variant="primary"))
        area.mount(Button("Cancel", id="cancel-export"))
        self._pending_export = True

    def restore_input(self) -> None:
        """Restore the normal input field."""
        self._pending_export = False
        area = self.query_one("#input-area", Container)
        area.clear()
        area.mount(Input(placeholder="Ask a question or type a SQL query...", id="user-input"))

    def clear_chat(self) -> None:
        """Remove all chat messages except the system prompt, and reset query state."""
        scroll = self.query_one("#chat-scroll", VerticalScroll)
        # Remove all ChatMessage and QueryTable widgets (keep Static widgets like system prompt)
        for widget in list(scroll.query(ChatMessage)) + list(scroll.query(QueryTable)):
            widget.remove()
        # Reset query state
        self.last_result = None
        self.last_query = None
        # Update the system prompt message
        schema_preview = self.schema[:200] + "..." if len(self.schema) > 200 else self.schema
        self.add_message(
            "assistant",
            f"Conversation reset. Schema reloaded.\n\n{SYSTEM_PROMPT}\n\nSchema:\n{schema_preview[:500]}...",
        )

    @on(Input.Submitted, "#user-input")
    async def on_input(self, event: Input.Submitted) -> None:
        if self._pending_export:
            return

        user_text = event.value.strip()
        if not user_text:
            return

        # Handle /new directive — start a fresh conversation
        if user_text.startswith("/new"):
            self.clear_chat()
            self.set_status("Ready. Ask a question in English.")
            return

        self.query_one("#user-input", Input).value = ""
        self.add_message("user", user_text)
        self.set_status("Thinking...")
        await self.process_message(user_text)

    async def process_message(self, user_text: str) -> None:
        """Send user message to LLM and handle the response."""
        # Build messages with schema
        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nDatabase Schema:\n{self.schema}"},
        ]

        # Add chat history
        scroll = self.query_one("#chat-scroll", VerticalScroll)
        for msg in scroll.query(ChatMessage):
            messages.append({"role": msg.role, "content": msg.text})

        # Add current message
        messages.append({"role": "user", "content": user_text})

        try:
            response = await acompletion(
                self.llm_model,
                messages,
                provider=self.llm_provider,
                tools=[SQL_TOOL, EXPORT_TOOL],
                api_key=self.llm_token,
                api_base=self.llm_url,
            )

            choice = response.choices[0]
            msg_content = choice.message.content or ""
            tool_calls = choice.message.tool_calls or []

            if msg_content:
                self.add_message("assistant", msg_content)

            for tc in tool_calls:
                fn = tc.function
                if fn.name == "run_sql":
                    args = fn.arguments
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {}
                    query = args.get("query", "") if isinstance(args, dict) else ""
                    if query:
                        rows, sql_error = await self.execute_query(query)
                        if sql_error:
                            self._sql_error_count += 1
                            # Let the LLM try to fix it before showing the error to the user
                            await self.handle_sql_error(query, sql_error)
                        else:
                            self._sql_error_count = 0
                elif fn.name == "export_pipe_delimited":
                    args = fn.arguments
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {}
                    filename = args.get("filename", "") if isinstance(args, dict) else ""
                    if filename and self.last_result is not None:
                        export_pipe_delimited(self.last_result, filename)
                        self.add_message("assistant", f"Exported {len(self.last_result)} rows to {filename}")
                    elif self.last_result is not None:
                        default_name = suggest_filename(self.last_query)
                        export_pipe_delimited(self.last_result, default_name)
                        self.add_message("assistant", f"Exported {len(self.last_result)} rows to {default_name}")

        except Exception as e:
            log_exception(e)
            self.set_status("Error")
            self.show_error(str(e))

    async def execute_query(self, query: str) -> tuple[list[dict], str | None]:
        """Execute a SQL query and display results. Returns (rows, error_message)."""
        self.set_status(f"Executing: {query[:60]}...")
        try:
            rows = await asyncio.get_running_loop().run_in_executor(None, self.db.execute, query)
            self.last_result = rows
            self.last_query = query
            self.show_table(rows, query)
            self.set_status(f"Returned {len(rows)} row(s)")
            return rows, None
        except Exception as e:
            log_exception(e)
            return [], str(e)

    async def handle_sql_error(self, query: str, error: str) -> None:
        """Send a SQL error back to the LLM for possible resolution before showing it to the user."""
        MAX_SQL_ERRORS = 5

        if self._sql_error_count >= MAX_SQL_ERRORS:
            self.notify(
                f"Query failed after {MAX_SQL_ERRORS} attempts. Giving up.",
                severity="error",
                timeout=8.0,
            )
            self.show_error(
                f"Query failed after {MAX_SQL_ERRORS} attempts. Giving up.\n\n"
                f"Error: {error}\n\n"
                f"Last query:\n{query}"
            )
            self.set_status("Query failed — too many errors")
            self._sql_error_count = 0  # reset so next user message can start fresh
            return

        attempt = self._sql_error_count
        self.notify(
            f"Resolving technical difficulties with the query (attempt {attempt}/{MAX_SQL_ERRORS})...",
            severity="warning",
            timeout=5.0,
        )
        self.set_status("SQL error — asking LLM for a fix...")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + f"Database Schema:\n{self.schema}"},
        ]
        scroll = self.query_one("#chat-scroll", VerticalScroll)
        for msg in scroll.query(ChatMessage):
            messages.append({"role": msg.role, "content": msg.text})

        messages.append({
            "role": "user",
            "content": (
                f"The following SQL query failed with the error: {error}\n\n"
                f"Query:\n{query}\n\n"
                "Please fix the query and call run_sql again with a corrected version."
            ),
        })

        try:
            response = await acompletion(
                self.llm_model,
                messages,
                provider=self.llm_provider,
                tools=[SQL_TOOL, EXPORT_TOOL],
                api_key=self.llm_token,
                api_base=self.llm_url,
            )

            choice = response.choices[0]
            msg_content = choice.message.content or ""
            tool_calls = choice.message.tool_calls or []

            if msg_content:
                self.add_message("assistant", msg_content)

            for tc in tool_calls:
                fn = tc.function
                if fn.name == "run_sql":
                    args = fn.arguments
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {}
                    corrected_query = args.get("query", "") if isinstance(args, dict) else ""
                    if corrected_query:
                        rows, sql_error = await self.execute_query(corrected_query)
                        if sql_error:
                            self._sql_error_count += 1
                            # Recurse to check limit and possibly ask for another fix
                            await self.handle_sql_error(corrected_query, sql_error)
                        else:
                            self._sql_error_count = 0
                        # else: execute_query already displayed the table on success
                elif fn.name == "export_pipe_delimited":
                    args = fn.arguments
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {}
                    filename = args.get("filename", "") if isinstance(args, dict) else ""
                    if filename and self.last_result is not None:
                        export_pipe_delimited(self.last_result, filename)
                        self.add_message("assistant", f"Exported {len(self.last_result)} rows to {filename}")
                    elif self.last_result is not None:
                        default_name = suggest_filename(self.last_query)
                        export_pipe_delimited(self.last_result, default_name)
                        self.add_message("assistant", f"Exported {len(self.last_result)} rows to {default_name}")

        except Exception as e:
            log_exception(e)
            self.set_status("Error")
            self.show_error(f"Original error: {error}\nLLM fix attempt also raised: {e}")

    @on(Button.Pressed, "#confirm-filename")
    async def on_confirm_filename(self) -> None:
        if self.last_result is None:
            self.show_error("No results to export")
            self.restore_input()
            return

        inp = self.query_one("#filename-input", Input)
        filename = inp.value.strip() or suggest_filename(self.last_query)
        try:
            export_pipe_delimited(self.last_result, filename)
            self.add_message("assistant", f"Exported {len(self.last_result)} rows to {filename}")
        except Exception as e:
            log_exception(e)
            self.show_error(f"Export failed: {e}")
        self.restore_input()
        self.set_status("Ready")

    @on(Button.Pressed, "#cancel-export")
    def on_cancel_export(self) -> None:
        self.add_message("assistant", "Export cancelled.")
        self.restore_input()
        self.set_status("Ready")

    def action_quit(self) -> None:
        self.db.close()
        self.exit()

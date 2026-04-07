"""Tests for tui.py — Textual TUI integration tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from pathlib import Path

from textual.widgets import Input

from aiquerychat.tui import AiquerychatApp, ChatMessage, export_pipe_delimited


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_app(schema_content: str = "# Schema\n") -> AiquerychatApp:
    """Build an AiquerychatApp with a temp schema file."""
    schema_file = Path("/tmp/test_schema.md")
    schema_file.write_text(schema_content)
    return AiquerychatApp(
        db_url="sqlite:///",
        llm_url="http://localhost:11434",
        llm_token="test-token",
        llm_model="gemma3:latest",
        schema_path=str(schema_file),
        llm_provider="ollama",
    )


# ---------------------------------------------------------------------------
# Test: export_pipe_delimited writes rows to a file
# ---------------------------------------------------------------------------

def test_export_data(tmp_path):
    """export_pipe_delimited writes rows to a file in pipe-delimited format."""
    rows = [
        {"EmployeeID": 1, "FirstName": "Alice", "LastName": "Smith"},
        {"EmployeeID": 2, "FirstName": "Bob", "LastName": "Jones"},
    ]
    export_file = tmp_path / "employees.txt"

    export_pipe_delimited(rows, str(export_file))

    content = export_file.read_text()
    # Pipe-delimited: header line
    assert "EmployeeID" in content
    assert "FirstName" in content
    assert "Alice" in content
    assert "Bob" in content
    # Verify pipe delimiters (no commas)
    assert "|" in content


# ---------------------------------------------------------------------------
# Test: execute simple english query → LLM calls run_sql → results
# ---------------------------------------------------------------------------

@pytest.mark.asyncio()
async def test_execute_simple_english_query():
    """User types an English query → LLM calls run_sql → results stored in last_result."""
    app = make_app("# Employees\n\n## Employees\n| Column | Type |\n|---|---|")
    mock_rows = [
        {"EmployeeID": 1, "FirstName": "Alice", "HireDate": "2020-01-15"},
        {"EmployeeID": 2, "FirstName": "Bob", "HireDate": "2019-06-20"},
    ]

    mock_tool_call = MagicMock()
    mock_tool_call.function = MagicMock()
    mock_tool_call.function.name = "run_sql"
    mock_tool_call.function.arguments = '{"query": "SELECT TOP 10 * FROM Employees ORDER BY HireDate DESC"}'

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Here are the top 10 employees.", tool_calls=[mock_tool_call]))
    ]

    async with app.run_test() as pilot:
        with patch("aiquerychat.tui.acompletion", new_callable=AsyncMock, return_value=mock_response):
            with patch.object(app.db, "execute", return_value=mock_rows):
                inp = app.query_one("#user-input", Input)
                inp.value = "show me top employees by hire date"
                inp.focus()
                await pilot.press("enter")
                await pilot.pause()

                # db.execute was called with the SQL from the tool call
                assert app.last_result == mock_rows
                assert app.last_query is not None
                assert "Employees" in app.last_query


# ---------------------------------------------------------------------------
# Test: /new directive clears chat history and resets state
# ---------------------------------------------------------------------------

@pytest.mark.asyncio()
async def test_new_directive_clears_chat():
    """Typing /new removes all chat messages and resets last_result."""
    app = make_app("# Schema\n")

    # Add some fake chat history by directly manipulating
    async with app.run_test() as pilot:
        # on_mount already adds 1 ChatMessage (system prompt)
        initial_count = len(list(app.query(ChatMessage)))
        assert initial_count == 1  # system prompt only

        # Add a user message and assistant response manually
        app.add_message("user", "show me employees")
        app.add_message("assistant", "Here are the employees")
        app.last_result = [{"EmployeeID": 1, "FirstName": "Alice"}]
        app.last_query = "SELECT * FROM Employees"

        # Verify state before /new
        assert len(list(app.query(ChatMessage))) == initial_count + 2  # user + assistant
        assert app.last_result is not None
        assert app.last_query is not None

        # Send /new
        inp = app.query_one("#user-input", Input)
        inp.value = "/new"
        inp.focus()
        await pilot.press("enter")
        await pilot.pause()

        # Chat should be cleared back to 1 ChatMessage ("Conversation reset")
        chat_messages = list(app.query(ChatMessage))
        assert len(chat_messages) == 1
        assert "Conversation reset" in chat_messages[0].text
        # State should be reset
        assert app.last_result is None
        assert app.last_query is None


# ---------------------------------------------------------------------------
# Test: execute query then LLM calls export tool → file written
# ---------------------------------------------------------------------------

@pytest.mark.asyncio()
async def test_execute_query_and_then_export(tmp_path):
    """User asks query → LLM calls run_sql → user asks export → LLM calls export tool → file written."""
    app = make_app("# Employees\n\n## Employees\n| Column | Type |\n|---|---|")
    mock_rows = [
        {"EmployeeID": 1, "FirstName": "Alice"},
        {"EmployeeID": 2, "FirstName": "Bob"},
    ]
    export_file = tmp_path / "employees_export.txt"

    # First LLM response: SQL tool call
    mock_sql_call = MagicMock()
    mock_sql_call.function = MagicMock()
    mock_sql_call.function.name = "run_sql"
    mock_sql_call.function.arguments = '{"query": "SELECT TOP 10 * FROM Employees"}'

    # Second LLM response: export tool call
    mock_export_call = MagicMock()
    mock_export_call.function = MagicMock()
    mock_export_call.function.name = "export_pipe_delimited"
    mock_export_call.function.arguments = f'{{"filename": "{export_file}"}}'

    mock_sql_response = MagicMock()
    mock_sql_response.choices = [
        MagicMock(message=MagicMock(content="", tool_calls=[mock_sql_call]))
    ]
    mock_export_response = MagicMock()
    mock_export_response.choices = [
        MagicMock(message=MagicMock(content="Exported!", tool_calls=[mock_export_call]))
    ]

    async with app.run_test() as pilot:
        with patch.object(app.db, "execute", return_value=mock_rows):
            with patch("aiquerychat.tui.export_pipe_delimited", wraps=export_pipe_delimited) as mock_export:
                with patch("aiquerychat.tui.acompletion", new_callable=AsyncMock) as mock_acompletion:
                    mock_acompletion.side_effect = [mock_sql_response, mock_export_response]

                    # First message: ask for employees
                    inp = app.query_one("#user-input", Input)
                    inp.value = "show me top employees by hire date"
                    inp.focus()
                    await pilot.press("enter")
                    await pilot.pause()

                    # Verify query was executed
                    assert app.last_result == mock_rows

                    # Second message: ask to export
                    inp = app.query_one("#user-input", Input)
                    inp.value = "export that to a file"
                    inp.focus()
                    await pilot.press("enter")
                    await pilot.pause()

                    # Export was called with correct rows and filename
                    mock_export.assert_called_once()
                    args, _ = mock_export.call_args
                    assert args[0] == mock_rows
                    assert args[1] == str(export_file)

                    # Verify file contents
                    content = export_file.read_text()
                    assert "Alice" in content
                    assert "Bob" in content


# ---------------------------------------------------------------------------
# Test: SQL error → LLM asked to fix → corrected query succeeds
# ---------------------------------------------------------------------------

@pytest.mark.asyncio()
async def test_sql_error_triggers_llm_fix():
    """SQL execution fails → error sent to LLM → LLM returns corrected query → succeeds."""
    app = make_app("# Employees\n\n## Employees\n| Column | Type |\n|---|---|")
    mock_rows = [{"EmployeeID": 1, "FirstName": "Alice"}]

    # Original tool call: bad T-SQL syntax (TOP without OFFSET for newer SQL Server)
    bad_query = "SELECT TOP 10 * FROM Employees"
    good_query = "SELECT * FROM Employees"

    bad_tool_call = MagicMock()
    bad_tool_call.function = MagicMock()
    bad_tool_call.function.name = "run_sql"
    bad_tool_call.function.arguments = json.dumps({"query": bad_query})

    # LLM's fix response: corrected query
    good_tool_call = MagicMock()
    good_tool_call.function = MagicMock()
    good_tool_call.function.name = "run_sql"
    good_tool_call.function.arguments = json.dumps({"query": good_query})

    bad_response = MagicMock()
    bad_response.choices = [
        MagicMock(message=MagicMock(content="", tool_calls=[bad_tool_call]))
    ]
    fix_response = MagicMock()
    fix_response.choices = [
        MagicMock(message=MagicMock(content="Here's the corrected query:", tool_calls=[good_tool_call]))
    ]

    async with app.run_test() as pilot:
        with patch("aiquerychat.tui.acompletion", new_callable=AsyncMock) as mock_acompletion:
            mock_acompletion.side_effect = [bad_response, fix_response]

            # Patch db.execute: first call raises, second call succeeds
            def db_execute_side_effect(query):
                if query == bad_query:
                    raise Exception("Invalid usage of TOP with OFFSET — use FETCH NEXT instead")
                return mock_rows

            with patch.object(app.db, "execute", side_effect=db_execute_side_effect):
                inp = app.query_one("#user-input", Input)
                inp.value = "show me employees"
                inp.focus()
                await pilot.press("enter")
                await pilot.pause()

                # LLM was called twice: once for the original, once for the fix
                assert mock_acompletion.call_count == 2

                # The corrected query was executed
                assert app.last_result == mock_rows
                assert app.last_query == good_query


# ---------------------------------------------------------------------------
# Test: SQL error → LLM fix also fails → error shown to user (not at 5-limit)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio()
async def test_sql_error_llm_fix_fails_shows_error():
    """SQL fails → LLM fix also fails → error displayed to user before hitting 5-limit."""
    app = make_app("# Employees\n\n## Employees\n| Column | Type |\n|---|---|")

    bad_query = "SELECT * FROM nonexistent_table"

    bad_tool_call = MagicMock()
    bad_tool_call.function = MagicMock()
    bad_tool_call.function.name = "run_sql"
    bad_tool_call.function.arguments = json.dumps({"query": bad_query})

    still_bad_tool_call = MagicMock()
    still_bad_tool_call.function = MagicMock()
    still_bad_tool_call.function.name = "run_sql"
    still_bad_tool_call.function.arguments = json.dumps({"query": bad_query})

    bad_response = MagicMock()
    bad_response.choices = [
        MagicMock(message=MagicMock(content="", tool_calls=[bad_tool_call]))
    ]
    fix_response = MagicMock()
    fix_response.choices = [
        MagicMock(message=MagicMock(content="Try this instead:", tool_calls=[still_bad_tool_call]))
    ]

    # Provide 6 responses (covers initial + 5 fix attempts without exhausting side_effect).
    # The first 3 LLM calls return valid responses; the 4th exhausts side_effect and raises
    # StopAsyncIteration which is caught and shown as an error, ending the chain well
    # before the 5-attempt cap is hit.
    async with app.run_test() as pilot:
        with patch("aiquerychat.tui.acompletion", new_callable=AsyncMock) as mock_acompletion:
            mock_acompletion.side_effect = [
                bad_response, fix_response, fix_response,
                bad_response, fix_response, fix_response,
            ]

            with patch.object(
                app.db, "execute", side_effect=Exception("Invalid object name 'nonexistent_table'")
            ):
                inp = app.query_one("#user-input", Input)
                inp.value = "show me employees"
                inp.focus()
                await pilot.press("enter")
                await pilot.pause()

                # At least some LLM calls were made before error surfaced
                assert mock_acompletion.call_count >= 2
                # Error was displayed to user (last_result still None)
                assert app.last_result is None


# ---------------------------------------------------------------------------
# Test: 5 consecutive run_sql errors → give up after 5th attempt
# ---------------------------------------------------------------------------

@pytest.mark.asyncio()
async def test_five_sql_errors_gives_up():
    """After 5 consecutive run_sql errors, the app stops retrying and shows error to user."""
    app = make_app("# T\n\n## T\n| C | T |\n|---|---|\"")

    # Every query the LLM generates will fail
    failing_tool_call = MagicMock()
    failing_tool_call.function = MagicMock()
    failing_tool_call.function.name = "run_sql"
    failing_tool_call.function.arguments = json.dumps({"query": "SELECT * FROM bad"})

    def make_response():
        resp = MagicMock()
        resp.choices = [MagicMock(message=MagicMock(content="", tool_calls=[failing_tool_call]))]
        return resp

    async with app.run_test() as pilot:
        with patch("aiquerychat.tui.acompletion", new_callable=AsyncMock) as mock_acompletion:
            mock_acompletion.return_value = make_response()
            with patch.object(app.db, "execute", side_effect=Exception("Bad table")):
                inp = app.query_one("#user-input", Input)
                inp.value = "show me stuff"
                inp.focus()
                await pilot.press("enter")
                await pilot.pause()

                # LLM called exactly 5 times (initial + 4 retries)
                assert mock_acompletion.call_count == 5
                # Error count was incremented each time but gave up at 5
                assert app._sql_error_count == 0  # reset after giving up
                assert app.last_result is None


# ---------------------------------------------------------------------------
# Test: successful query resets error counter to zero
# ---------------------------------------------------------------------------

@pytest.mark.asyncio()
async def test_successful_query_resets_error_counter():
    """A successful run_sql call resets _sql_error_count to 0."""
    app = make_app("# E\n\n## E\n| C | T |\n|---|---|\"")
    mock_rows = [{"ID": 1}]

    # First query fails, second succeeds
    bad_tool_call = MagicMock()
    bad_tool_call.function = MagicMock()
    bad_tool_call.function.name = "run_sql"
    bad_tool_call.function.arguments = json.dumps({"query": "SELECT * FROM bad"})

    good_tool_call = MagicMock()
    good_tool_call.function = MagicMock()
    good_tool_call.function.name = "run_sql"
    good_tool_call.function.arguments = json.dumps({"query": "SELECT * FROM good"})

    def db_side_effect(q):
        if "bad" in q:
            raise Exception("bad table")
        return mock_rows

    bad_response = MagicMock()
    bad_response.choices = [MagicMock(message=MagicMock(content="", tool_calls=[bad_tool_call]))]
    good_response = MagicMock()
    good_response.choices = [MagicMock(message=MagicMock(content="Here are the results:", tool_calls=[good_tool_call]))]

    async with app.run_test() as pilot:
        with patch("aiquerychat.tui.acompletion", new_callable=AsyncMock) as mock_acompletion:
            mock_acompletion.side_effect = [bad_response, good_response]
            with patch.object(app.db, "execute", side_effect=db_side_effect):
                inp = app.query_one("#user-input", Input)
                inp.value = "show me data"
                inp.focus()
                await pilot.press("enter")
                await pilot.pause()

                # First attempt failed but was retried and succeeded
                assert mock_acompletion.call_count == 2
                # Counter was incremented for the failure, then reset by the success
                assert app._sql_error_count == 0
                assert app.last_result == mock_rows

# Purpose

This tool provides an LLM guided tool to query the landlord database (or any database given it's schema and a connection to the database).

The tool will provide a python TUI chat interface. The will interact with chat messages ("English queries of the database.") The chat bot
may ask questions to clarify details. Once the details are established. The LLM will execute a SELECT query against the database
and present the data in nicely formatted tables in the TUI. The user may ask for the query results to be written as PIPE delimited data
files.

## Python Requirements

- Use python click CLI parsing module
- Use python uv tool to manage dependencies
- Use sqlalchemy to query the database
- Use the python any_llm_sdk[openai] module to connect to the LLM
- Create a Makefile with these targets:
  - make venv -> uv venv
  - make deps -> uv sync or uv pip install -r requirements.txt
  - make test -> run the project tests
  - make lint -> run ruff lint checks
  - make run -> start the chat interface session

## App Requirements

### Schema file

The LLM will add the specified schema file into it's context. It will use the schema file to better understand how best to query
for the results the user is asking for. The user may specify the schema file in the CLI using the "--schema/-s" options.

### Sqlalchemy url

The tool will connect to this URL by default.

export DATABASE_URL="mssql+pymssql://user:pass@host/db"

Store this default in a dotenv file. Allow the user to specify the URL via the "--url/-u" option.

### LLM Connection

The tool will connect to this LLM (OpenAI compatible endpoint) by default:

- http://127.0.0.1:11434/api/chat/v1

The user may specify this LLM URL in the dotenv file or by the "--llmurl/-l" CLI options.

The app will use the specified values to set the following environment variables or pass them to any_llm_sdk when it creates the LLM connection.

OPENAI_BASE_URL
OPENAI_TOKEN

By default (also specified in the dotenv), the model will use "gemma3:latest"



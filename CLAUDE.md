# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Run all tests:
```sh
uv run pytest
```

Run a single test file:
```sh
uv run pytest test_septa.py
```

Run a single test by name:
```sh
uv run pytest test_septa.py::test_process_response_extracts_trains
```

Run a script directly (dependencies auto-managed by uv):
```sh
uv run septa.py "Suburban Station"
```

## Architecture

Each utility is a self-contained script with inline `uv` dependency declarations at the top (`# /// script ... ///`). There is no shared library — scripts are independent and can be copied or run standalone.

**Script structure pattern** (follow this for new tools):
- `fetch_*`: hits an external API, returns raw data
- `process_*`: transforms raw data into domain objects/lists — this is what tests target
- `format_*` / `display_*`: formats for terminal output
- `main()`: wires args → fetch → process → display

Tests live in `test_<script_name>.py` alongside the script. Tests import directly from the script module (e.g. `from septa import process_response`). Tests mock at the network boundary (`requests.post`, `requests.get`) and test `process_*` functions with real data fixtures, not mocked internal calls.

**strava.py** fetches a Strava activity and starts an interactive terminal chat about it, using the `llm` Python API for a multi-turn conversation with the activity held in context. It uses the `stravalib` library and requires OAuth2 with token refresh, and relies on `llm`'s configured default model (override with `-m/--model`). Credentials (`STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`, and `OPENAI_API_KEY` for `llm`) load at startup from a gitignored `.env` via `python-dotenv` (see `.env.example`), falling back to real environment variables, which take precedence. `strava_prompts.py` holds the `SYSTEM_PROMPT` for the chat analysis. `test_strava.py` holds tests (currently token/URL helpers).

The chat is a small agent: it runs `llm`'s tool-calling loop (`model.conversation(tools=[...])` + `conversation.chain(...)`, which auto-executes tool calls and re-prompts until the model answers). `strava_tools.py` provides the `search_runlog` tool — a TF-IDF-ranked search (scikit-learn `TfidfVectorizer`) over the athlete's running log (`RUNLOG.txt`, override with `--runlog`) — built from pure `parse_runlog`/`search_entries`/`format_entries` helpers. Tests in `test_strava_tools.py` cover only the logic we wrote (parsing, the guard/`>0` filter/limit around the vectorizer, the no-match sentinel), not scikit-learn's ranking. BM25 is documented in-code as the next step. Note: with the default OpenAI plugin (Chat Completions), reasoning-model reasoning state is not preserved across turns — the model re-reasons each turn from the visible transcript, so tool results must be self-contained.

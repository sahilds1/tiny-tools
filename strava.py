#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "stravalib==2.4",
#     "llm==0.31",
#     "python-dotenv==1.0.1",
# ]
# ///

# Chat about Strava activities (by id, single date, or date range) in a conversation with an LLM

import argparse
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import llm
from dotenv import load_dotenv
from stravalib import Client

from strava_prompts import SYSTEM_PROMPT

TOKEN_PATH = Path.home() / ".strava_tokens.json"


def load_tokens(token_path: Path = TOKEN_PATH) -> dict | None:
    # TODO: Add logging
    if not token_path.exists():
        return None
    with open(token_path) as f:
        return json.load(f)


def save_tokens(tokens: dict, token_path: Path = TOKEN_PATH) -> None:
    # TODO: Add logging
    with open(token_path, "w") as f:
        json.dump(tokens, f)


def is_token_expired(token_data: dict) -> bool:
    return time.time() >= token_data["expires_at"]


def parse_code_from_url(redirect_url: str) -> str:
    parsed = urlparse(redirect_url)
    params = parse_qs(parsed.query)
    codes = params.get("code", [])
    if not codes:
        raise ValueError("No 'code' parameter found in the redirect URL")
    return codes[0]


def get_authenticated_client(client_id: int, client_secret: str) -> Client:
    """
    
    Parameters
    ----------
    
    Returns
    -------
    
    """
    client = Client()
    tokens = load_tokens()
    
    if tokens:

        if not is_token_expired(tokens):
            client.access_token = tokens["access_token"]
            return client
        else: 
            # Note: WARNING:root:Please set client.refresh_token if you want to usethe auto token-refresh feature
            token_response = client.refresh_access_token(
                client_id=client_id,
                client_secret=client_secret,
                refresh_token=tokens["refresh_token"],
            )
            save_tokens(dict(token_response))
            client.access_token = token_response["access_token"]
            return client
    else:
        # Full OAuth flow
        url = client.authorization_url(
            client_id=client_id,
            redirect_uri="http://127.0.0.1:5000/authorization",
        )
        print(f"\nOpen this URL in your browser to authorize:\n\n  {url}\n")
        redirect_url = input("Paste the full redirect URL here: ").strip()
        code = parse_code_from_url(redirect_url)
    
        token_response = client.exchange_code_for_token(
            client_id=client_id,
            client_secret=client_secret,
            code=code,
        )
        save_tokens(dict(token_response))
        client.access_token = token_response["access_token"]
        return client


def parse_date(s: str) -> datetime:
    """Parse a YYYY-MM-DD string into a midnight datetime (treated as UTC by Strava)."""
    return datetime.strptime(s, "%Y-%m-%d")


def fetch_activities_in_range(client: Client, after, before=None) -> list:
    """Return DetailedActivity objects for activities in the [after, before) window.

    get_activities only returns SummaryActivity, so wrap each summary with get_activity
    to upgrade it to the full DetailedActivity used for chat context.
    """
    # Note: with before=None this pulls every activity since `after` and makes one
    # get_activity call per match, which can be many requests on a wide window
    # (Strava rate-limits ~100 requests / 15 min).
    # TODO: Add a --limit cap to bound the number of activities (and API calls).
    summaries = client.get_activities(after=after, before=before)
    return [client.get_activity(s.id, include_all_efforts=True) for s in summaries]


def main():
    parser = argparse.ArgumentParser(description="Chat about Strava activities with an LLM")
    # Note: dates filter by UTC start date, which can differ from the athlete's local day.
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--id", type=int, help="Strava activity ID")
    selection.add_argument("--date", help="Activities on a single day (YYYY-MM-DD)")
    selection.add_argument("--start", help="Range start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="Range end date (YYYY-MM-DD, inclusive); requires --start")
    parser.add_argument(
        "-m",
        "--model",
        default=None,
        help="llm model to use (default: your configured llm default model)",
    )
    args = parser.parse_args()

    if args.end and not args.start:
        parser.error("--end requires --start")

    # Load STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, and OPENAI_API_KEY from a local .env
    # (gitignored; see .env.example) so they don't have to be exported in the shell.
    #
    # Precedence / priority of these variables:
    # - load_dotenv() does NOT override variables already set in the real environment, so an
    #   existing `export FOO=...` in your shell wins over the .env value. Unset the shell var
    #   if you want .env to be the source of truth.
    # - This must run before llm.get_model() below: the OpenAI key is never read by this
    #   script directly — `llm` reads OPENAI_API_KEY from the environment, so it only sees
    #   the .env value once load_dotenv() has populated os.environ.
    # - `llm` checks its own keystore (`llm keys set openai`) BEFORE the OPENAI_API_KEY env
    #   var, so a key stored there would take priority over anything in .env.
    load_dotenv()

    client_id = os.environ.get("STRAVA_CLIENT_ID")
    client_secret = os.environ.get("STRAVA_CLIENT_SECRET")
    if not client_id or not client_secret:
        parser.error(
            "Set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET in the environment "
            "or in a .env file (see .env.example)."
        )
    client_id = int(client_id)

    client = get_authenticated_client(client_id, client_secret)

    # Resolve the selection into a list of DetailedActivity objects.
    # TODO: Add typing for activities list[stravalib.model.DetailedActivity]
    if args.id is not None:
        activities = [client.get_activity(args.id, include_all_efforts=True)]
    elif args.date:
        after = parse_date(args.date)
        activities = fetch_activities_in_range(client, after, after + timedelta(days=1))
    else:
        after = parse_date(args.start)
        before = parse_date(args.end) + timedelta(days=1) if args.end else None
        activities = fetch_activities_in_range(client, after, before)

    if not activities:
        print("No activities found for that selection.")
        return

    # Drop the raw activities (pydantic models) into the LLM context as a JSON list.
    # TODO: Replace with a curated format_activity() that converts to a human-readable
    # summary (km/mi, pace, splits, best efforts) and serves as a testable format_* seam.
    # TODO: Include time-series streams (HR, pace, power) via client.get_activity_streams()
    # for richer per-second data in the chat analysis.
    context = json.dumps([a.model_dump(mode="json") for a in activities], indent=2)

    # Drive the chat with the `llm` Python API
    # (https://llm.datasette.io/en/stable/python-api.html):
    # - llm.get_model(None) returns llm's configured default model; -m/--model overrides it,
    #   so this script relies on whatever model/key the user has set up via `llm`.
    # - model.conversation() is a multi-turn object that retains history automatically, so
    #   follow-up questions keep the context of earlier turns (and the activity below).
    model = llm.get_model(args.model)
    conversation = model.conversation()

    # Seed the activity into context via the system prompt so it's available without a
    # round-trip — nothing is sent until the user asks a question.
    # TODO: Optionally print an initial analysis automatically before the loop, e.g.
    # conversation.prompt(context, system=SYSTEM_PROMPT) and stream the response.
    system = f"{SYSTEM_PROMPT}\n\nStrava activities (JSON):\n{context}"

    print(f"Chatting about {len(activities)} activit{'y' if len(activities) == 1 else 'ies'}. "
          "Ask a question ('exit' or Ctrl-D to quit).")
    first_turn = True
    
    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break

        # conversation.prompt() sends the turn to the model; the system prompt (carrying the
        # activity) is passed only on the first turn, since the conversation retains history.

        if first_turn:
            response = conversation.prompt(user_input, system=system)
        else:
            response = conversation.prompt(user_input)

        first_turn = False

        # response.text() resolves and returns the full reply as a single string.
        # Alternative: an llm response is iterable, so you can stream each text chunk as it
        # arrives with `for chunk in response: print(chunk, end="", flush=True)`.
        print(response.text())


if __name__ == "__main__":
    main()

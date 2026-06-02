#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "stravalib==2.4",
#     "llm==0.31",
# ]
# ///

# Output Strava activity to analyze in a Chat conversation

import argparse
import json
import os
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import llm
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


def main():
    parser = argparse.ArgumentParser(description="Chat about a Strava activity with an LLM")
    parser.add_argument("activity_id", type=int, help="Strava activity ID")
    parser.add_argument(
        "-m",
        "--model",
        default=None,
        help="llm model to use (default: your configured llm default model)",
    )
    args = parser.parse_args()

    # TOOD: Read the  STRAVA CLIENT ID and STRAVA CLIENT SECRET enviornment variables from a file
    client_id = int(os.environ["STRAVA_CLIENT_ID"])
    client_secret = os.environ["STRAVA_CLIENT_SECRET"]

    client = get_authenticated_client(client_id, client_secret)

    # TODO: Add typing for activity stravalib.model.DetailedActivity
    activity = client.get_activity(args.activity_id, include_all_efforts=True)

    # Drop the raw activity (a pydantic model) into the LLM context as JSON.
    # TODO: Replace with a curated format_activity() that converts to a human-readable
    # summary (km/mi, pace, splits, best efforts) and serves as a testable format_* seam.
    # TODO: Include time-series streams (HR, pace, power) via client.get_activity_streams()
    # for richer per-second data in the chat analysis.
    context = activity.model_dump_json(indent=2)

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
    system = f"{SYSTEM_PROMPT}\n\nStrava activity (JSON):\n{context}"

    print(f"Chatting about activity {args.activity_id}. Ask a question ('exit' or Ctrl-D to quit).")
    first = True
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
        response = conversation.prompt(user_input, system=system) if first else conversation.prompt(user_input)
        first = False

        # An llm response is iterable: looping over it streams text chunks as they arrive.
        for chunk in response:
            print(chunk, end="", flush=True)
        print()


if __name__ == "__main__":
    main()

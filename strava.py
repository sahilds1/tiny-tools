#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "stravalib==2.4",
# ]
# ///

# Output Strava activity to analyze in a Chat conversation

import argparse
import json
import os
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from stravalib import Client

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
    parser = argparse.ArgumentParser(description="Output a Strava activity for chat analysis")
    parser.add_argument("activity_id", type=int, help="Strava activity ID")
    args = parser.parse_args()

    # TOOD: Read the  STRAVA CLIENT ID and STRAVA CLIENT SECRET enviornment variables from a file
    client_id = int(os.environ["STRAVA_CLIENT_ID"])
    client_secret = os.environ["STRAVA_CLIENT_SECRET"]

    client = get_authenticated_client(client_id, client_secret)

    # TODO: Add typing for activity stravalib.model.DetailedActivity
    activity = client.get_activity(args.activity_id, include_all_efforts=True)

    # TODO: format_activity — format key fields (distance, pace, splits, HR, best efforts)
    # into a readable text block for pasting into a chat conversation.
    # TODO: Include time-series streams (HR, pace, power) via client.get_activity_streams()
    # for richer per-second data in the chat analysis.
    # TODO: Pipe output through an LLM using strava_prompts.py
    # (similar to how llm_commit_message.py works) and print the analysis directly.
    print(activity)


if __name__ == "__main__":
    main()

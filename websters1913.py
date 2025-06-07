#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "bs4",
#     "requests",
# ]
# ///

# Output word definitions from websters1913.com

import argparse

import requests
from bs4 import BeautifulSoup


def fetch_definition(word: str) -> list[str]:
    url = f"https://www.websters1913.com/words/{word}"
    response = requests.get(url)

    if response.status_code != 200:
        raise RuntimeError(
            f"Error: Unable to fetch definition (status code {response.status_code})"
        )

    soup = BeautifulSoup(response.text, "html.parser")
    def_tags = soup.select("def")

    if not def_tags:
        return [f"No definition found for '{word}' on Websters1913."]

    return [tag.get_text(strip=True) for tag in def_tags]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch word definitions from websters1913.com"
    )
    parser.add_argument("--word", help="The word to define")
    args = parser.parse_args()

    try:
        definitions = fetch_definition(args.word)
        # TODO: Strip out newlines and extra spaces from definitions

        print(f"\nDefinitions for '{args.word}':\n")
        for index, definition in enumerate(definitions):
            print(f"{index + 1}. {definition}")
    except Exception as e:
        print(str(e))

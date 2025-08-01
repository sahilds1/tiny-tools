#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "bs4",
#     "requests",
# ]
# ///

# Output word definitions from websters1913.com
# TODO: Consider rate liming to be respectful to the website
# TODO: Add caching for repeated lookups

import argparse
import logging

import requests
from bs4 import BeautifulSoup, ResultSet, Tag

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_definition(word: str) -> ResultSet[Tag]:
    logging.info(f"Fetching definition for word: '{word}'")
    url = f"https://www.websters1913.com/words/{word}"
    logging.debug(f"Making request to URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Network connection failed")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP error: {e}")
    except requests.exceptions.Timeout:
        raise RuntimeError("Request timed out")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request error: {e}")

    # Websters1913 uses <def> tags
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        def_tags = soup.select("def")
        return def_tags
    except Exception as e:
        raise RuntimeError(f"Failed to parse HTML: {e}")


if __name__ == "__main__":
    logging.info("Starting websters1913 dictionary lookup")
    parser = argparse.ArgumentParser(
        description="Fetch word definitions from websters1913.com"
    )
    parser.add_argument("--word", required=True, help="The word to define")
    args = parser.parse_args()

    # TODO: Write intput validation as a function for testing
    word = args.word.strip()
    if not word:
        raise ValueError("Word cannot be empty or whitespace")

    def_tags = fetch_definition(word)

    if not def_tags:
        raise RuntimeError(f"No definition found for '{word}' on Websters1913.")

    # TODO: Write retrieval  of defintions into a function for testing
    definitions = [tag.get_text(strip=True) for tag in def_tags]
    logging.info(f"Successfully retrieved {len(definitions)} definitions for '{word}'")

    print(f"\nDefinitions for '{word}':\n")
    for index, definition in enumerate(definitions):
        clean_definition = " ".join(definition.split())
        print(f"{index + 1}. {clean_definition}")

    logging.info("Dictionary lookup completed successfully")

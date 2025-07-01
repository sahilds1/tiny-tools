# Generate a commit message based on a diff input

import argparse
import sys

from openai import OpenAI


def generate_commit_message(diff: str) -> str:
    """Generate a commit message based on the provided diff."""

    client = OpenAI()

    response = client.responses.create(
        model="gpt-4.1-nano",
        instructions="Draft a commit message based on the provided diff.",
        input=diff,
    )

    return response.output_text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Input file (default: stdin)",
    )
    args = parser.parse_args()

    print(generate_commit_message(args.input.read()))

# /// script
# dependencies = [
#   "openai==1.83.0"
# ]
# ///

# Generate a commit message based on a diff input

import argparse
import sys

from openai import OpenAI

INSTRUCTIONS = """
Generate a commit message based on the provided diff.
The commit message should be a single line and should be a short description of the changes.
The commit message should be in the following format:
<type>: <description>
The type should be one of the following:

ADD adding new feature
FIX a bug
DOC documentation only
REF refactoring that doesn't include any changes in features 
FMT formatting only (spacing...)
MAK repository related changes (e.g., changes in the ignore list)
TEST related to test code only.
"""


def generate_commit_message(diff: str) -> str:
    """Generate a commit message based on the provided diff."""

    client = OpenAI()

    response = client.responses.create(
        model="gpt-4.1-nano",
        instructions=INSTRUCTIONS,
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

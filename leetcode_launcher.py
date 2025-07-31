#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests",
# ]
# ///

# Open a LeetCode problem from its number

import webbrowser
import argparse
import logging

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def get_problem_slug(problem_number: str) -> str:
    """
    Get the title slug of a LeetCode problem from its number

    Parameters
    ----------
    problem_number: str

    Returns
    -------
    str
    """
    logging.info(f"Fetching problem slug for problem #{problem_number}")

    url = "https://leetcode.com/graphql/"
    headers = {"Content-Type": "application/json"}

    # TODO: Added a fallback search method that looks for exact matches by questionFrontendId.
    payload = {
        "query": """
        query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
            problemsetQuestionList: questionList(
                categorySlug: $categorySlug
                limit: $limit
                skip: $skip
                filters: $filters
            ) {
                questions: data {
                    titleSlug
                }
            }
        }
        """,
        "variables": {
            "categorySlug": "all-code-essentials",
            "skip": 0,
            "limit": 20,
            "filters": {"searchKeywords": f"{problem_number}"},
        },
        "operationName": "problemsetQuestionList",
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
    except requests.RequestException as e:
        raise requests.RequestException(
            f"Network error fetching problem {problem_number}: {e}"
        )

    try:
        # TODO: Fetching 20 results but only using the first one
        response_data = response.json()
        questions = response_data["data"]["problemsetQuestionList"]["questions"]
        logging.info(f"Found {len(questions)} matching problems")
        title_slug = questions[0]["titleSlug"]
        logging.info(f"Using problem slug: {title_slug}")
    except IndexError:
        raise IndexError(f"Empty response for problem {problem_number}")
    except TypeError:
        raise TypeError(f"Malformed response for problem {problem_number}")

    return title_slug


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Open a LeetCode problem by its number"
    )
    parser.add_argument(
        "--num", type=int, required=True, help="LeetCode problem number"
    )
    args = parser.parse_args()

    # Additional validation for reasonable range
    if args.num <= 0:
        parser.error(f"Problem number must be positive, got: {args.num}")

    title_slug = get_problem_slug(args.num)

    problem_url = f"https://leetcode.com/problems/{title_slug}"
    logging.info(f"Opening LeetCode problem URL: {problem_url}")
    webbrowser.open(problem_url)
    logging.info("Successfully opened problem in browser")

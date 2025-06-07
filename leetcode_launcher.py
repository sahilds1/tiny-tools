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

import requests


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

    # TODO: Check for errors in the response because GraphQL always returns 200
    url = "https://leetcode.com/graphql/"

    headers = {"Content-Type": "application/json"}

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

    response = requests.post(url, json=payload, headers=headers)

    # Decode into a dictionary using response.json()
    title_slug = response.json()["data"]["problemsetQuestionList"]["questions"][0][
        "titleSlug"
    ]

    return title_slug


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Open a LeetCode problem by its number"
    )
    parser.add_argument("--num", required=True, help="LeetCode problem number")
    args = parser.parse_args()

    title_slug = get_problem_slug(args.num)

    webbrowser.open(f"https://leetcode.com/problems/{title_slug}")

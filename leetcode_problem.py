# Open a LeetCode problem from its number

import webbrowser
import argparse

import requests

def get_problem_slug(problem_number: str) -> str:
    """
    Get the tile slug of a LeetCode problem from its number

    Parameters
    ----------
    problem_number: str

    Returns
    -------
    str
    """

    url = "https://leetcode.com/graphql/"
    # TODO: Read about Headers
    headers = {
        "Content-Type": "application/json"
    }
    # TODO: Read about GraphQL query
    # TODO: Avoid unnecessary keys in the GraphQL query. Many fields in the response (acRate, difficulty, freqBar, etc.) are unused.
    payload = {
        "query": """
        query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
            problemsetQuestionList: questionList(
                categorySlug: $categorySlug
                limit: $limit
                skip: $skip
                filters: $filters
            ) {
                total: totalNum
                questions: data {
                    acRate
                    difficulty
                    freqBar
                    frontendQuestionId: questionFrontendId
                    isFavor
                    paidOnly: isPaidOnly
                    status
                    title
                    titleSlug
                    topicTags {
                        name
                        id
                        slug
                    }
                    hasSolution
                    hasVideoSolution
                }
            }
        }
        """,
        "variables": {
            "categorySlug": "all-code-essentials",
            "skip": 0,
            #TODO: Read about reducing limit to optimize performance
            "limit": 20,
            "filters": {
                "searchKeywords": f"{problem_number}"
            }
        },
        "operationName": "problemsetQuestionList"
    }

    try:
        #TODO: Read the requests.post API documentation   
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request error: {e}")

    # TODO: Add error handling for no problem found for problem number or unexpected response format
    try:
        # Decode into a dictionary using response.json() 
        title_slug = response.json()['data']['problemsetQuestionList']['questions'][0]['titleSlug']
    except Exception as e:
        raise RuntimeError(f"Response error: {e}")
        
    return title_slug

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Open a LeetCode problem by its number")
    parser.add_argument("--num", required=True, help="LeetCode problem number")
    args = parser.parse_args()

    title_slug = get_problem_slug(args.num)

    webbrowser.open(f"https://leetcode.com/problems/{title_slug}")
# Load LeetCode by Problem Number

import requests
# TODO: Write a TIL on webbrowser 

#The webbrowser module provides a high-level interface to allow displaying web-based documents to users. Under most circumstances, simply calling the open() function from this module will do the right thing.

#The script webbrowser can be used as a command-line interface for the module. It accepts a URL as the argument. It accepts the following optional parameters:

# -n/--new-window opens the URL in a new browser window, if possible.

# -t/--new-tab opens the URL in a new browser page (“tab”).

# The options are, naturally, mutually exclusive. Usage example:

# python -m webbrowser -t "https://www.python.org"
import webbrowser


url = "https://leetcode.com/graphql/"
# TODO: Read about Headers
headers = {
    "Content-Type": "application/json"
}
# TODO: Read about GraphQL query
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
        "limit": 20,
        "filters": {
            "searchKeywords": "1346"
        }
    },
    "operationName": "problemsetQuestionList"
}

#TODO: Add  check that the request was successful 
#TODO: Read the requests.post API documentation   
response = requests.post(url, json=payload, headers=headers)

#Decode into a dictionary using response.json() 
title_slug = response.json()['data']['problemsetQuestionList']['questions'][0]['titleSlug']

webbrowser.open(f"https://leetcode.com/problems/{title_slug}")
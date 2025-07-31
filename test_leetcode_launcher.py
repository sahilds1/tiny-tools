from unittest.mock import patch, Mock

import pytest
import requests

from leetcode_launcher import get_problem_slug


class TestGetProblemSlug:
    @patch("leetcode_launcher.requests.post")
    def test_get_problem_slug_success(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "problemsetQuestionList": {
                    "questions": [{"questionFrontendId": "1", "titleSlug": "two-sum"}]
                }
            }
        }
        mock_post.return_value = mock_response

        result = get_problem_slug("1")

        assert result == "two-sum"
        mock_post.assert_called_once()

    @patch("leetcode_launcher.requests.post")
    def test_get_problem_slug_network_error(self, mock_post):
        mock_post.side_effect = requests.RequestException("Network error")

        with pytest.raises(requests.RequestException):
            get_problem_slug("1")

    @patch("leetcode_launcher.requests.post")
    def test_get_problem_slug_empty_response(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {"problemsetQuestionList": {"questions": []}}
        }
        mock_post.return_value = mock_response

        with pytest.raises(IndexError, match="Empty response for problem 999999"):
            get_problem_slug("999999")

    @patch("leetcode_launcher.requests.post")
    def test_get_problem_slug_malformed_response(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"data": None}
        mock_post.return_value = mock_response

        with pytest.raises(TypeError):
            get_problem_slug("1")

    @patch("leetcode_launcher.requests.post")
    def test_get_problem_slug_exact_match_with_multiple_results(self, mock_post):
        """Test that the function finds the exact questionFrontendId match among multiple results"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "problemsetQuestionList": {
                    "questions": [
                        {
                            "questionFrontendId": "10",
                            "titleSlug": "regular-expression-matching",
                        },
                        {"questionFrontendId": "1", "titleSlug": "two-sum"},
                        {"questionFrontendId": "100", "titleSlug": "same-tree"},
                        {
                            "questionFrontendId": "1000",
                            "titleSlug": "minimum-cost-to-merge-stones",
                        },
                    ]
                }
            }
        }
        mock_post.return_value = mock_response

        result = get_problem_slug("1")

        assert result == "two-sum"
        mock_post.assert_called_once()

    @patch("leetcode_launcher.requests.post")
    def test_get_problem_slug_no_exact_match(self, mock_post):
        """Test that the function raises IndexError when no exact questionFrontendId match is found"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "problemsetQuestionList": {
                    "questions": [
                        {
                            "questionFrontendId": "10",
                            "titleSlug": "regular-expression-matching",
                        },
                        {"questionFrontendId": "100", "titleSlug": "same-tree"},
                        {
                            "questionFrontendId": "1000",
                            "titleSlug": "minimum-cost-to-merge-stones",
                        },
                    ]
                }
            }
        }
        mock_post.return_value = mock_response

        with pytest.raises(IndexError, match="No exact match found for problem 1"):
            get_problem_slug("1")

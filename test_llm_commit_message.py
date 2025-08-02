from unittest.mock import patch, Mock, ANY

import pytest

from llm_commit_message import generate_commit_message


class TestGenerateCommitMessage:
    @patch("llm_commit_message.openai.OpenAI")
    def test_generate_commit_message_success(self, mock_openai_class):
        mock_client = Mock()
        mock_response = Mock()
        mock_response.output_text = "ADD: Implement user authentication"
        mock_client.responses.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        diff = """
        +def authenticate_user(username, password):
        +    return verify_credentials(username, password)
        """

        result = generate_commit_message(diff)

        assert result == "ADD: Implement user authentication"
        mock_client.responses.create.assert_called_once_with(
            model="gpt-4.1-nano", instructions=ANY, input=diff
        )

    @patch("llm_commit_message.openai.OpenAI")
    def test_generate_commit_message_api_connection_error(self, mock_openai_class):
        import openai

        mock_client = Mock()
        mock_client.responses.create.side_effect = openai.APIConnectionError(
            request=Mock()
        )
        mock_openai_class.return_value = mock_client

        with pytest.raises(RuntimeError, match="The server could not be reached"):
            generate_commit_message("some diff")

    @patch("llm_commit_message.openai.OpenAI")
    def test_generate_commit_message_rate_limit_error(self, mock_openai_class):
        import openai

        mock_client = Mock()
        mock_client.responses.create.side_effect = openai.RateLimitError(
            "Rate limit exceeded", response=Mock(), body=None
        )
        mock_openai_class.return_value = mock_client

        with pytest.raises(RuntimeError, match="A 429 status code was received"):
            generate_commit_message("some diff")

    @patch("llm_commit_message.openai.OpenAI")
    def test_generate_commit_message_api_status_error(self, mock_openai_class):
        import openai

        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_client.responses.create.side_effect = openai.APIStatusError(
            "Server error", response=mock_response, body=None
        )
        mock_openai_class.return_value = mock_client

        with pytest.raises(RuntimeError, match="A 500 status code was recieved"):
            generate_commit_message("some diff")

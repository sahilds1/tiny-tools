from unittest.mock import patch, Mock

import pytest
import requests

from websters1913 import fetch_definition


class TestFetchDefinition:
    @patch("websters1913.requests.get")
    def test_fetch_definition_success(self, mock_get):
        mock_response = Mock()
        mock_response.text = (
            "<html><def>A feeling of deep sympathy and sorrow</def></html>"
        )
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_definition("pathos")

        assert len(result) == 1
        assert result[0].get_text(strip=True) == "A feeling of deep sympathy and sorrow"
        mock_get.assert_called_once_with(
            "https://www.websters1913.com/words/pathos", timeout=10
        )

    @patch("websters1913.requests.get")
    def test_fetch_definition_multiple_definitions(self, mock_get):
        mock_response = Mock()
        mock_response.text = """<html>
            <def>First definition</def>
            <def>Second definition</def>
        </html>"""
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_definition("test")

        assert len(result) == 2
        assert result[0].get_text(strip=True) == "First definition"
        assert result[1].get_text(strip=True) == "Second definition"

    @patch("websters1913.requests.get")
    def test_fetch_definition_no_definitions(self, mock_get):
        mock_response = Mock()
        mock_response.text = "<html><p>No definitions here</p></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_definition("nonexistent")

        assert len(result) == 0

    @patch("websters1913.requests.get")
    def test_fetch_definition_404_error(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Client Error"
        )
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError, match="HTTP error: 404 Client Error"):
            fetch_definition("notfound")

    @patch("websters1913.requests.get")
    def test_fetch_definition_500_error(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "500 Server Error"
        )
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError, match="HTTP error: 500 Server Error"):
            fetch_definition("error")

    @patch("websters1913.requests.get")
    def test_fetch_definition_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError(
            "Network connection failed"
        )

        with pytest.raises(RuntimeError, match="Network connection failed"):
            fetch_definition("word")

    @patch("websters1913.requests.get")
    def test_fetch_definition_timeout_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        with pytest.raises(RuntimeError, match="Request timed out"):
            fetch_definition("word")

    @patch("websters1913.requests.get")
    def test_fetch_definition_request_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException(
            "Generic request error"
        )

        with pytest.raises(RuntimeError, match="Request error: Generic request error"):
            fetch_definition("word")

    @patch("websters1913.requests.get")
    def test_fetch_definition_with_whitespace(self, mock_get):
        mock_response = Mock()
        mock_response.text = "<html><def>  Definition with spaces  </def></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_definition("word")

        assert len(result) == 1
        assert result[0].get_text(strip=True) == "Definition with spaces"

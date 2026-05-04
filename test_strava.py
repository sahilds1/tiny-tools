import time

import pytest

from strava import is_token_expired, parse_code_from_url


def test_is_token_expired_when_expired():
    tokens = {"expires_at": time.time() - 1}
    assert is_token_expired(tokens) is True


def test_is_token_expired_when_valid():
    tokens = {"expires_at": time.time() + 3600}
    assert is_token_expired(tokens) is False


def test_parse_code_from_url():
    url = "http://127.0.0.1:5000/authorization?state=&code=abc123&scope=read,activity:read_all"
    assert parse_code_from_url(url) == "abc123"


def test_parse_code_from_url_missing_code():
    url = "http://127.0.0.1:5000/authorization?state=&scope=read"
    with pytest.raises(ValueError, match="No 'code' parameter"):
        parse_code_from_url(url)

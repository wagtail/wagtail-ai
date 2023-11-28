import pytest
from wagtail_ai import tokens


def test_get_default_token_limit_for_known_model():
    assert tokens.get_default_token_limit("gpt-3.5-turbo") == 4096


def test_get_default_token_limit_for_unknown_model():
    with pytest.raises(tokens.NoTokenLimitFound, match="echo-123-16k"):
        tokens.get_default_token_limit("echo-123-16k")

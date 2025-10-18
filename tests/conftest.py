import types
from typing import Callable, Dict, Generator

import pytest

from wagtail_ai.models import Prompt

TEST_PROMPT_LABEL = "Prompt Label"
TEST_PROMPT_VALUE = "Prompt Text"
TEST_PROMPT_DESCRIPTION = "Prompt Text"


@pytest.fixture
def test_prompt_values() -> Dict[str, str]:
    return {
        "label": TEST_PROMPT_LABEL,
        "description": TEST_PROMPT_DESCRIPTION,
        "prompt": TEST_PROMPT_VALUE,
        "method": Prompt.Method.REPLACE.value,
    }


@pytest.fixture
def setup_prompt_object(test_prompt_values: Dict[str, str]) -> Generator[Prompt, None, None]:
    prompt = Prompt.objects.create(**test_prompt_values)

    yield prompt

    prompt.delete()


@pytest.fixture(autouse=True)
def temporary_media(settings, tmp_path) -> None:
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def get_soup() -> Callable[[str | bytes], object]:
    from bs4 import BeautifulSoup

    def _get_soup(markup: str | bytes):
        # Ensure we pass a str to BeautifulSoup - decode bytes if necessary.
        if isinstance(markup, (bytes, bytearray)):
            markup = markup.decode()

        # Use an empty string_containers argument so that <script>, <style>, and
        # <template> tags do not have their text ignored.
        return BeautifulSoup(markup, "html.parser", string_containers={})

    return _get_soup


@pytest.fixture
def image_data_url() -> str:
    return (
        "data:image/gif;base64,"
        "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
    )

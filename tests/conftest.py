import types
from typing import Callable, Dict, Generator, TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    # Imported only for type checking to avoid importing Django models at
    # module import time which triggers Django app loading before pytest
    # config has a chance to set up the test settings.
    from wagtail_ai.models import Prompt
    from bs4 import BeautifulSoup  # For type hints only


# Ensure Django is configured and apps are loaded as early as possible when
# pytest imports this conftest module. Many package modules import Django
# models at import time which will fail unless Django settings are configured
# and apps are loaded. We set a default test settings module and call
# django.setup() here; this is safe for test runs and will be ignored when
# running static checks or when Django isn't available.
import os
try:
    if "DJANGO_SETTINGS_MODULE" not in os.environ:
        os.environ["DJANGO_SETTINGS_MODULE"] = "testapp.settings"

    import django
    from django.apps import apps

    django.setup()

    if not apps.is_installed("django_ai_core"):
        raise ImportError("django_ai_core is not installed")

    # Import our agents to register them before any URL patterns are resolved
    from wagtail_ai.agents.basic_prompt import BasicPromptAgent  # noqa
    from wagtail_ai.agents.content_feedback import ContentFeedbackAgent  # noqa 
    from wagtail_ai.agents.suggested_content import SuggestedContentAgent  # noqa
except Exception as e:
    # Ignore failures here; the test run will surface configuration errors
    # later in a clearer way if Django isn't available or settings fail to
    # import.
    print(f"Setup error: {e}")

TEST_PROMPT_LABEL = "Prompt Label"
TEST_PROMPT_VALUE = "Prompt Text"
TEST_PROMPT_DESCRIPTION = "Prompt Text"


@pytest.fixture
def test_prompt_values() -> Dict[str, str]:
    # Import Prompt lazily to avoid importing Django models at module import
    # time (which would attempt to access Django settings/apps). The import
    # happens when the fixture is executed during test setup.
    from wagtail_ai.models import Prompt

    return {
        "label": TEST_PROMPT_LABEL,
        "description": TEST_PROMPT_DESCRIPTION,
        "prompt": TEST_PROMPT_VALUE,
        "method": Prompt.Method.REPLACE.value,
    }


@pytest.fixture
def setup_prompt_object(test_prompt_values: Dict[str, str]) -> Generator["Prompt", None, None]:
    # Lazily import Prompt so Django models are not imported during conftest
    # import. Importing inside the fixture keeps module import-time safe and
    # still allows type checking via TYPE_CHECKING above.
    from wagtail_ai.models import Prompt

    prompt = Prompt.objects.create(**test_prompt_values)

    yield prompt

    prompt.delete()


@pytest.fixture(autouse=True)
def temporary_media(settings, tmp_path) -> None:
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def get_soup() -> Callable[[str | bytes], "BeautifulSoup"]:
    from bs4 import BeautifulSoup

    def _get_soup(markup: str | bytes) -> BeautifulSoup:
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

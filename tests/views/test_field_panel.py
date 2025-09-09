import json

import pytest
from bs4 import BeautifulSoup, Tag
from django.urls import reverse

from wagtail_ai.prompts import DefaultPrompt

pytestmark = pytest.mark.django_db


def test_search_description_uses_ai_field_panel(admin_client, get_soup):
    url = reverse("wagtailadmin_pages:edit", args=[2])
    response = admin_client.get(url)
    assert response.status_code == 200
    soup: BeautifulSoup = get_soup(response.content)
    input = soup.select_one('[name="search_description"]')
    assert input is not None

    # Input must be controlled by the FieldPanelController
    panel = input.find_parent(attrs={"data-controller": "wai-field-panel"})
    assert isinstance(panel, Tag)
    assert panel.get("data-wai-field-panel-prompts-value") == json.dumps(
        [DefaultPrompt.DESCRIPTION]
    )

    # There must be a template for the dropdown to be rendered by the controller
    template = soup.select_one("template#wai-field-panel-dropdown-template")
    assert template is not None
    dropdown = template.select_one('[data-controller~="w-dropdown"]')
    assert dropdown is not None

    # Ensure CSS classes are applied
    assert "wai-dropdown" in dropdown["class"]
    toggle = dropdown.select_one(".wai-dropdown__toggle")
    assert toggle is not None


def test_title_uses_ai_field_panel(admin_client, get_soup):
    url = reverse("wagtailadmin_pages:edit", args=[2])
    response = admin_client.get(url)
    assert response.status_code == 200
    soup: BeautifulSoup = get_soup(response.content)
    input = soup.select_one('[name="title"]')
    assert input is not None
    assert input.get("data-controller") == "w-sync"

    # Input must be controlled by the FieldPanelController
    panel = input.find_parent(attrs={"data-controller": "wai-field-panel"})
    assert isinstance(panel, Tag)
    assert (classname := panel.get("class")) is not None
    assert "title" in classname

    # There must be a template for the dropdown to be rendered by the controller
    template = soup.select_one("template#wai-field-panel-dropdown-template")
    assert template is not None
    dropdown = template.select_one('[data-controller~="w-dropdown"]')
    assert dropdown is not None

    # Ensure CSS classes are applied
    assert "wai-dropdown" in dropdown["class"]
    toggle = dropdown.select_one(".wai-dropdown__toggle")
    assert toggle is not None

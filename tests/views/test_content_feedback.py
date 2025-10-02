import pytest
from bs4 import BeautifulSoup, Tag
from django.templatetags.static import static
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_content_feedback_section_rendered_in_checks_panel(admin_client, get_soup):
    url = reverse("wagtailadmin_pages:edit", args=[2])
    response = admin_client.get(url)
    assert response.status_code == 200
    soup: BeautifulSoup = get_soup(response.content)
    panel = soup.select_one('[data-side-panel="checks"]')
    assert panel is not None

    # Ensure static files are included
    styles = panel.select_one(
        f"""link[href="{static('wagtail_ai/content_feedback.css')}"]"""
    )
    assert isinstance(styles, Tag)
    script = panel.select_one(
        f"""script[src="{static('wagtail_ai/content_feedback.js')}"]"""
    )
    assert isinstance(script, Tag)

    # Ensure the feedback controller is present
    controller = panel.select_one('[data-controller="wai-feedback"]')
    assert isinstance(controller, Tag)
    assert controller.get("data-wai-feedback-url-value") == reverse(
        "wagtail_ai:content_feedback"
    )

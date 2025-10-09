import json
from http import HTTPStatus
from typing import cast
from unittest.mock import ANY, Mock, call

import pytest
from bs4 import BeautifulSoup
from django.contrib.auth.models import Permission, User
from django.forms import Textarea
from django.urls import reverse
from wagtail.images.models import Image
from wagtail_factories import ImageFactory

from wagtail_ai.agents.basic_prompt import ImageDescriptionPrompt, ImageTitlePrompt
from wagtail_ai.ai import echo
from wagtail_ai.forms import ImageDescriptionWidgetMixin

pytestmark = pytest.mark.django_db


def test_get_request(admin_client):
    response = admin_client.get(reverse("wagtail_ai:describe_image"))
    assert response.status_code == 400
    assert response.json() == {"error": "This field is required."}


def test_image_not_found(admin_client):
    response = admin_client.post(
        reverse("wagtail_ai:describe_image"), data={"image_id": 1}
    )
    assert response.status_code == 404


def test_access_denied(client):
    user = User.objects.create_user(username="test")
    user.user_permissions.add(Permission.objects.get(codename="access_admin"))
    client.force_login(user)
    image = cast(Image, ImageFactory())
    response = client.post(
        reverse("wagtail_ai:describe_image"), data={"image_id": image.pk}
    )
    assert response.status_code == 403
    assert response.json() == {"error": "Access denied."}


def test_backend_not_configured(settings, admin_client):
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "echo": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {
                    "MODEL_ID": "echo",
                    "TOKEN_LIMIT": 123123,
                },
            },
        },
    }

    image = cast(Image, ImageFactory())
    response = admin_client.post(
        reverse("wagtail_ai:describe_image"), data={"image_id": image.pk}
    )
    assert response.status_code == 400
    assert response.json() == {
        "error": (
            "No backend is configured for image description. Please set"
            " `IMAGE_DESCRIPTION_BACKEND` in `settings.WAGTAIL_AI`."
        ),
    }


def test_success(admin_client, settings):
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "echo": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {
                    "MODEL_ID": "echo",
                    "TOKEN_LIMIT": 123123,
                },
            },
        },
        "IMAGE_DESCRIPTION_BACKEND": "echo",
    }

    image = cast(Image, ImageFactory())
    response = admin_client.post(
        reverse("wagtail_ai:describe_image"), data={"image_id": image.pk}
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "This is an echo backend: images/example.max-800x600.jpg"
    }


def test_custom_prompt(admin_client, settings, monkeypatch: pytest.MonkeyPatch):
    describe_image = Mock(return_value=echo.EchoResponse(iter([])))
    monkeypatch.setattr(echo.EchoBackend, "describe_image", describe_image)

    CUSTOM_PROMPT = "Other prompt"
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "echo": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {
                    "MODEL_ID": "echo",
                    "TOKEN_LIMIT": 123123,
                },
            },
        },
        "IMAGE_DESCRIPTION_BACKEND": "echo",
        "IMAGE_DESCRIPTION_PROMPT": CUSTOM_PROMPT,
    }

    image = cast(Image, ImageFactory())
    admin_client.post(reverse("wagtail_ai:describe_image"), data={"image_id": image.pk})
    assert describe_image.call_args == call(image_file=ANY, prompt=CUSTOM_PROMPT)


def test_custom_rendition_filter(admin_client, settings):
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "echo": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {
                    "MODEL_ID": "echo",
                    "TOKEN_LIMIT": 123123,
                },
            },
        },
        "IMAGE_DESCRIPTION_BACKEND": "echo",
        "IMAGE_DESCRIPTION_RENDITION_FILTER": "max-100x100",
    }

    image = cast(Image, ImageFactory())
    response = admin_client.post(
        reverse("wagtail_ai:describe_image"), data={"image_id": image.pk}
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "This is an echo backend: images/example.max-100x100.jpg"
    }


@pytest.mark.parametrize(
    "maxlength,expected_status,error_message",
    [
        (100, HTTPStatus.OK, None),
        (
            -1,
            HTTPStatus.BAD_REQUEST,
            "Ensure this value is greater than or equal to 0.",
        ),
        (
            10000,
            HTTPStatus.BAD_REQUEST,
            "Ensure this value is less than or equal to 4096.",
        ),
    ],
)
def test_maxlength_validation(
    admin_client, settings, maxlength, expected_status, error_message
):
    settings.WAGTAIL_AI = {
        "BACKENDS": {
            "echo": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {
                    "MODEL_ID": "echo",
                    "TOKEN_LIMIT": 123123,
                },
            },
        },
        "IMAGE_DESCRIPTION_BACKEND": "echo",
    }

    image = cast(Image, ImageFactory())
    response = admin_client.post(
        reverse("wagtail_ai:describe_image"),
        data={"image_id": image.pk, "maxlength": maxlength},
    )
    assert response.status_code == expected_status
    if error_message is not None:
        assert response.json() == {"error": error_message}


def test_enabled_on_image_upload(admin_client, get_soup):
    url = reverse("wagtailimages:add")
    response = admin_client.get(url)
    assert response.status_code == 200

    soup: BeautifulSoup = get_soup(response.content)
    form = soup.select_one("main form")
    assert form is not None

    title = form.select_one('[name="title"]')
    assert title is not None
    assert title.get("data-controller") == "wai-field-panel"
    assert title.get("maxlength") == "255"
    assert title.has_attr("data-wai-field-panel-image-id") is False
    assert title.get("data-wai-field-panel-image-input-value") == "#id_file"
    assert title.get("data-wai-field-panel-prompts-value") == json.dumps(
        [ImageTitlePrompt.name]
    )

    description = form.select_one('[name="description"]')
    assert description is not None
    assert description.get("data-controller") == "wai-field-panel"
    assert description.get("maxlength") == "255"
    assert title.has_attr("data-wai-field-panel-image-id") is False
    assert description.get("data-wai-field-panel-image-input-value") == "#id_file"
    assert description.get("data-wai-field-panel-prompts-value") == json.dumps(
        [ImageDescriptionPrompt.name]
    )


def test_enabled_on_image_edit(admin_client, get_soup):
    image = cast(Image, ImageFactory())
    url = reverse("wagtailimages:edit", args=[image.pk])
    response = admin_client.get(url)
    assert response.status_code == 200

    soup: BeautifulSoup = get_soup(response.content)
    form = soup.select_one("main form")
    assert form is not None

    title = form.select_one('[name="title"]')
    assert title is not None
    assert title.get("data-controller") == "wai-field-panel"
    assert title.get("maxlength") == "255"
    assert title.has_attr("data-wai-field-panel-image-id") is True
    assert title.get("data-wai-field-panel-image-id") == str(image.pk)
    assert title.get("data-wai-field-panel-image-input-value") == "#id_file"
    assert title.get("data-wai-field-panel-prompts-value") == json.dumps(
        [ImageTitlePrompt.name]
    )

    description = form.select_one('[name="description"]')
    assert description is not None
    assert description.get("data-controller") == "wai-field-panel"
    assert description.get("maxlength") == "255"
    assert title.has_attr("data-wai-field-panel-image-id") is True
    assert description.get("data-wai-field-panel-image-id") == str(image.pk)
    assert description.get("data-wai-field-panel-image-input-value") == "#id_file"
    assert description.get("data-wai-field-panel-prompts-value") == json.dumps(
        [ImageDescriptionPrompt.name]
    )


def test_image_description_widget_with_textarea(get_soup):
    class ImageDescriptionTextarea(ImageDescriptionWidgetMixin, Textarea):
        pass

    html = ImageDescriptionTextarea(
        image_id=123,
        file_selector="#id_file",
        attrs={"maxlength": "512"},
    ).render("description", "A portrait of a Wagtail.")
    soup: BeautifulSoup = get_soup(html)

    textarea = soup.select_one('textarea[name="description"]')
    assert textarea is not None
    assert textarea.get("data-controller") == "wai-field-panel"
    assert textarea.get("maxlength") == "512"
    assert textarea.get("data-wai-field-panel-image-id") == "123"
    assert textarea.get("data-wai-field-panel-image-input-value") == "#id_file"
    assert textarea.get("data-wai-field-panel-prompts-value") == json.dumps(
        [ImageDescriptionPrompt.name]
    )
    assert textarea.text.strip() == "A portrait of a Wagtail."

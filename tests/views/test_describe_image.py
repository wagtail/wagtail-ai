from typing import cast
from unittest.mock import ANY, Mock, call

import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse
from wagtail.images.models import Image
from wagtail_factories import ImageFactory

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
    assert response.json() == {"error": "Access denied"}


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
    from wagtail_ai.ai import echo

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

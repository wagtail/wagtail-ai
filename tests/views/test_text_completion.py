import uuid

import pytest
from django.urls import reverse

from wagtail_ai.views import PromptEditForm, prompt_viewset

pytestmark = pytest.mark.django_db


def test_prompt_model_admin_form_validation(test_prompt_values):
    form_data = {
        "label": test_prompt_values["label"],
        "description": test_prompt_values["description"],
        "prompt": test_prompt_values["prompt"],
        "method": "foo",  # Invalid method value
    }
    form = PromptEditForm(data=form_data)
    assert not form.is_valid()
    assert "method" in form.errors


def test_prompt_model_admin_viewset_list_view(admin_client, setup_prompt_object):
    url = reverse(f"{prompt_viewset.url_prefix}:index")
    response = admin_client.get(url)
    assert response.status_code == 200
    assert setup_prompt_object.label in str(response.content)


def test_prompt_model_admin_viewset_edit_view(admin_client, setup_prompt_object):
    url = reverse(f"{prompt_viewset.url_prefix}:edit", args=[setup_prompt_object.id])
    response = admin_client.get(url)
    assert response.status_code == 200
    assert setup_prompt_object.label in str(response.content)


def test_process_view_get_request(admin_client):
    url = reverse("wagtail_ai:text_completion")

    response = admin_client.get(url)
    assert response.status_code == 400
    assert response.json() == {
        "error": "No text provided - please enter some text before using AI features. "
        "\nInvalid prompt provided."
    }


def test_process_view_post_without_text(admin_client):
    url = reverse("wagtail_ai:text_completion")

    response = admin_client.post(url, data={})
    assert response.status_code == 400
    assert response.json() == {
        "error": "No text provided - please enter some text before using AI features. "
        "\nInvalid prompt provided."
    }


@pytest.mark.parametrize(
    "prompt", [None, "NOT-A-UUID", str(uuid.uuid1()), str(uuid.uuid4())]
)
def test_process_view_with_bad_prompt_id(admin_client, prompt):
    url = reverse("wagtail_ai:text_completion")

    data = {"text": "test"}
    if prompt is not None:
        data["prompt"] = prompt

    response = admin_client.post(url, data=data)
    assert response.status_code == 400
    assert response.json() == {"error": "Invalid prompt provided."}


def test_process_view_with_correct_prompt(admin_client, setup_prompt_object):
    url = reverse("wagtail_ai:text_completion")

    response = admin_client.post(
        url, data={"text": "test", "prompt": str(setup_prompt_object.uuid)}
    )
    assert response.status_code == 200
    # correct, the tests default is the echo backend
    assert response.json() == {"message": "This is an echo backend: test"}

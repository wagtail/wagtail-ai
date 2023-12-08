import pytest
from django.urls import reverse
from wagtail_ai.views import PromptEditForm, prompt_viewset


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


@pytest.mark.django_db
def test_prompt_model_admin_viewset_list_view(client, setup_users, setup_prompt_object):
    url = reverse(f"{prompt_viewset.url_prefix}:index")
    superuser = setup_users
    client.force_login(superuser)
    response = client.get(url)
    assert response.status_code == 200
    assert setup_prompt_object.label in str(response.content)


@pytest.mark.django_db
def test_prompt_model_admin_viewset_edit_view(client, setup_users, setup_prompt_object):
    url = reverse(f"{prompt_viewset.url_prefix}:edit", args=[setup_prompt_object.id])
    superuser = setup_users
    client.force_login(superuser)
    response = client.get(url)
    assert response.status_code == 200
    assert setup_prompt_object.label in str(response.content)


# TODO add tests for process view

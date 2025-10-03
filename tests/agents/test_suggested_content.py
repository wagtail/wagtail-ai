import json
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest
from django.http import HttpResponse
from django.urls import reverse
from django_ai_core.contrib.index import registry as index_registry
from wagtail.admin.admin_url_finder import AdminURLFinder


@dataclass
class MockPage:
    pk: int
    title: str


@pytest.fixture
def mock_vector_index():
    mock_instance = MagicMock()
    MockVectorIndexClass = MagicMock(return_value=mock_instance)

    with (
        patch.object(index_registry, "get", return_value=MockVectorIndexClass),
        patch.object(AdminURLFinder, "get_edit_url", return_value="/admin/"),
    ):
        yield mock_instance


@pytest.mark.django_db
def test_responds_with_data(admin_client, mock_vector_index):
    pages = [MockPage(pk=0, title="Foo")]
    expected_data = [{"id": 0, "title": "Foo", "editUrl": "/admin/"}]
    mock_vector_index.search_sources.return_value = pages

    response: HttpResponse = admin_client.post(
        reverse("wagtail_ai:suggested_content"),
        data=json.dumps(
            {
                "arguments": {
                    "vector_index": "PageIndex",
                    "chunk_size": 1000,
                    "content": "foo",
                    "current_page_pk": 1,
                    "limit": 3,
                }
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    content = json.loads(response.content.decode())
    assert content["data"] == expected_data


@pytest.mark.django_db
def test_excludes_current_pk(admin_client, mock_vector_index):
    pages = [MockPage(pk=0, title="Foo"), MockPage(pk=1, title="Bar")]
    expected_data = [{"id": 0, "title": "Foo", "editUrl": "/admin/"}]
    mock_vector_index.search_sources.return_value = pages

    response: HttpResponse = admin_client.post(
        reverse("wagtail_ai:suggested_content"),
        data=json.dumps(
            {
                "arguments": {
                    "vector_index": "PageIndex",
                    "chunk_size": 1000,
                    "content": "foo",
                    "current_page_pk": 1,
                    "limit": 3,
                }
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    content = json.loads(response.content.decode())
    assert content["data"] == expected_data


@pytest.mark.django_db
def test_applies_limit(admin_client, mock_vector_index):
    pages = [
        MockPage(pk=0, title="Foo"),
        MockPage(pk=1, title="Bar"),
        MockPage(pk=2, title="Baz"),
        MockPage(pk=3, title="Quz"),
    ]
    mock_vector_index.search_sources.return_value = pages

    response: HttpResponse = admin_client.post(
        reverse("wagtail_ai:suggested_content"),
        data=json.dumps(
            {
                "arguments": {
                    "vector_index": "PageIndex",
                    "chunk_size": 1000,
                    "content": "foo",
                    "current_page_pk": 10,
                    "limit": 3,
                }
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    content = json.loads(response.content.decode())
    assert len(content["data"]) == 3


@pytest.mark.django_db
def test_applies_limit_excluding_current_pk(admin_client, mock_vector_index):
    pages = [
        MockPage(pk=0, title="Foo"),
        MockPage(pk=1, title="Bar"),
        MockPage(pk=2, title="Baz"),
        MockPage(pk=3, title="Quz"),
        MockPage(pk=4, title="Buz"),
    ]
    mock_vector_index.search_sources.return_value = pages

    response: HttpResponse = admin_client.post(
        reverse("wagtail_ai:suggested_content"),
        data=json.dumps(
            {
                "arguments": {
                    "vector_index": "PageIndex",
                    "chunk_size": 1000,
                    "content": "foo",
                    "current_page_pk": 1,
                    "limit": 3,
                }
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    content = json.loads(response.content.decode())
    assert len(content["data"]) == 3
    assert content["data"][1]["id"] == 2


@pytest.mark.django_db
def test_chunks_provided_content(admin_client, mock_vector_index):
    content = ["word " * 1000]

    response: HttpResponse = admin_client.post(
        reverse("wagtail_ai:suggested_content"),
        data=json.dumps(
            {
                "arguments": {
                    "vector_index": "PageIndex",
                    "chunk_size": 1000,
                    "content": content,
                    "current_page_pk": 1,
                    "limit": 3,
                }
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    mock_vector_index.search_sources.assert_called_with(content[:1000])

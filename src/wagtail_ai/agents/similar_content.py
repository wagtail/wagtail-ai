from django_ai_core.contrib.agents import (
    Agent,
    AgentParameter,
)
from django_ai_core.contrib.agents import (
    registry as agent_registry,
)
from django_ai_core.contrib.index import registry as index_registry
from wagtail.admin.admin_url_finder import AdminURLFinder


@agent_registry.register()
class SimilarContentAgent(Agent):
    slug = "wai_similar_content"
    description = "Suggests similar content to the provided context using the provided VectorIndex"
    parameters = [
        AgentParameter(
            name="vector_index",
            type=str,
            description="ID of the VectorIndex to query",
        ),
        AgentParameter(
            name="current_page_pk", type=int, description="PK of the current page"
        ),
        AgentParameter(
            name="content",
            type=str,
            description="Content to use in similarity search",
        ),
        AgentParameter(
            name="limit",
            type=int,
            description="Number of responses to return",
        ),
    ]

    def execute(
        self, vector_index: str, current_page_pk: int, content: str, limit: int = 3
    ) -> list:
        index_cls = index_registry.get(vector_index)
        index = index_cls()
        finder = AdminURLFinder()
        # Extend limit by 1 in case we get the current page in the response
        extended_limit = limit + 1

        return [
            {"id": page.pk, "title": page.title, "editUrl": finder.get_edit_url(page)}
            for page in index.search_sources(content)[:extended_limit]
            if page.pk != current_page_pk
        ][:limit]

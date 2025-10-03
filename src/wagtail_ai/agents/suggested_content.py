from django_ai_core.contrib.agents import (
    Agent,
    AgentParameter,
)
from django_ai_core.contrib.agents import (
    registry as agent_registry,
)
from django_ai_core.contrib.index import registry as index_registry
from django_ai_core.contrib.index.chunking import SimpleChunkTransformer
from wagtail.admin.admin_url_finder import AdminURLFinder


@agent_registry.register()
class SuggestedContentAgent(Agent):
    slug = "wai_suggested_content"
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
        AgentParameter(
            name="chunk_size",
            type=int,
            description="Number of characters to embed from content",
        ),
    ]

    def execute(
        self,
        vector_index: str,
        current_page_pk: int,
        content: str,
        limit: int = 3,
        chunk_size: int = 1000,
    ) -> list:
        index_cls = index_registry.get(vector_index)
        index = index_cls()
        finder = AdminURLFinder()
        # Extend limit by 1 in case we get the current page in the response
        extended_limit = limit + 1

        if not chunk_size:
            chunk_size = 1000

        chunk_transformer = SimpleChunkTransformer(chunk_size=chunk_size)
        chunks = chunk_transformer.transform(content)

        return [
            {"id": page.pk, "title": page.title, "editUrl": finder.get_edit_url(page)}
            for page in index.search_sources(chunks[0])[:extended_limit]
            if page.pk != current_page_pk
        ][:limit]

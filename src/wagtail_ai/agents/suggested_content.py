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

MAX_LIMIT = 100


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
            name="exclude_pks",
            type=list[str],
            description="PKs to exclude from results",
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
        exclude_pks: list[str],
        content: str,
        limit: int = 3,
        chunk_size: int = 1000,
    ) -> list:
        index_cls = index_registry.get(vector_index)
        index = index_cls()
        finder = AdminURLFinder()
        # Extend limit by the number of excluded PKs so we get enough responses
        extended_limit = limit + len(exclude_pks)

        if extended_limit > MAX_LIMIT:
            return []

        if not chunk_size:
            chunk_size = 1000

        chunk_transformer = SimpleChunkTransformer(chunk_size=chunk_size)
        chunks = chunk_transformer.transform(content)

        if not chunks:
            return []

        return [
            {
                "id": str(page.pk),
                "title": page.title,
                "editUrl": finder.get_edit_url(page),
            }
            for page in index.search_sources(chunks[0])[:extended_limit]
            if str(page.pk) not in exclude_pks
        ][:limit]

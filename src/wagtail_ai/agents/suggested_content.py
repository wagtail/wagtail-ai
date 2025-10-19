"""Suggested content agent module.

This module provides an agent that suggests similar content based on a vector
index search. Imports are done lazily to avoid import-time side effects from
third-party packages when the module is imported during pytest collection.
"""

from wagtail.admin.admin_url_finder import AdminURLFinder


def _lazy_imports():
    """Perform imports lazily to avoid import-time side effects from
    third-party packages (django_ai_core, queryish, etc.) when the package
    is imported by pytest during collection.
    """
    from django_ai_core.contrib.agents import (
        Agent,
        AgentParameter,
    )
    from django_ai_core.contrib.agents import registry as agent_registry
    from django_ai_core.contrib.index import registry as index_registry
    from django_ai_core.contrib.index.chunking import SimpleChunkTransformer

    return Agent, AgentParameter, agent_registry, index_registry, SimpleChunkTransformer


MAX_LIMIT = 100


Agent, AgentParameter, agent_registry, index_registry, SimpleChunkTransformer = _lazy_imports()


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


# Register the agent with django-ai-core
agent_registry.register()(SuggestedContentAgent)

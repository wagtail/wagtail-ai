from dataclasses import dataclass
from typing import Optional, Type

from wagtail_ai.vector_backends import Backend, VectorIndex
from wagtail_ai.vector_backends.qdrant.client import QdrantClient


@dataclass
class BackendConfig:
    HOST: str
    API_KEY: Optional[str] = None


class QdrantBackend(Backend[BackendConfig]):
    config_class = BackendConfig

    def __init__(self, config):
        super().__init__(config)
        self.client = QdrantClient(host=self.config.HOST, api_key=self.config.API_KEY)

    def _build_index(self, index_class: Type[VectorIndex]):
        index = index_class()
        index_name = index_class.__name__
        self.client.delete_collection(name=index_name)
        self.client.create_collection(
            name=index_name,
            vector_size=self.ai_backend.embedding_dimensions,
        )

        for entry in index.get_entries():
            self.client.add_point(
                collection_name=index_name,
                id=entry["id"],
                vector=entry["vector"],
                payload=entry["metadata"],
            )

    def rebuild_indexes(self):
        for index_class in self._get_indexes():
            self._build_index(index_class)

    def search(self, index_class, query):
        query_embedding = self.ai_backend.get_embedding(query)
        return self.client.search(
            collection_name=index_class.__name__, vector=query_embedding
        )

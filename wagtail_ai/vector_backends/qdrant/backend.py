from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, List, Optional

from wagtail_ai.vector_backends import Backend

from .client import QdrantClient


if TYPE_CHECKING:
    from wagtail_ai.index import VectorIndex


@dataclass
class BackendConfig:
    HOST: str
    API_KEY: Optional[str] = None


class QdrantBackend(Backend[BackendConfig]):
    config_class = BackendConfig

    def __init__(self, config):
        super().__init__(config)
        self.client = QdrantClient(host=self.config.HOST, api_key=self.config.API_KEY)

    def _build_index(self, index: "VectorIndex"):
        index_name = index.get_name()
        self.client.delete_collection(name=index_name)
        self.client.create_collection(
            name=index_name,
            vector_size=self.ai_backend.embedding_dimensions,
        )

        for document in index.get_documents():
            self.client.add_point(
                collection_name=index_name,
                id=document.id,
                vector=document.vector,
                payload=asdict(document.metadata),
            )

    def rebuild_indexes(self):
        for index in self._get_indexes():
            self._build_index(index)

    def search(
        self, index: "VectorIndex", query_embedding, *, limit: int = 5
    ) -> List[dict]:
        similar_documents = self.client.search(
            collection_name=index.get_name(), vector=query_embedding, limit=limit
        )
        return [doc["payload"] for doc in similar_documents]

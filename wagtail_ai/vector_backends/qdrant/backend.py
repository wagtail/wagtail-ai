from dataclasses import asdict, dataclass
from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from wagail_ai.index import Document

from wagtail_ai.vector_backends import Backend, Index, SearchResponseDocument


@dataclass
class BackendConfig:
    HOST: str
    API_KEY: Optional[str] = None


class QdrantIndex(Index):
    def __init__(self, index_name: str, api_client: QdrantClient):
        self.index_name = index_name
        self.client = api_client

    def upsert(self, *, documents: List[Document]):
        points = [
            qdrant_models.PointStruct(
                id=document.id,
                vector=document.vector,
                payload=asdict(document.metadata),
            )
            for document in documents
        ]
        self.client.upsert(collection_name=self.index_name, points=points)

    def delete(self, *, document_ids: List[str]):
        self.client.delete(
            collection_name=self.index_name,
            points_selector=qdrant_models.PointIdsList(points=document_ids),
        )

    def similarity_search(self, query_vector, *, limit: int = 5):
        similar_documents = self.client.search(
            collection_name=self.index_name, query_vector=query_vector, limit=limit
        )
        return [
            SearchResponseDocument(id=doc["id"], metadata=doc["payload"])
            for doc in similar_documents
        ]


class QdrantBackend(Backend[BackendConfig, QdrantIndex]):
    config_class = BackendConfig

    def __init__(self, config):
        super().__init__(config)
        self.client = QdrantClient(url=self.config.HOST, api_key=self.config.API_KEY)

    def get_index(self, index_name) -> QdrantIndex:
        return QdrantIndex(index_name, api_client=self.client)

    def create_index(self, index_name, *, vector_size: int) -> QdrantIndex:
        self.client.create_collection(
            name=index_name,
            vectors_config=qdrant_models.VectorParams(
                size=vector_size, distance="Cosine"
            ),
        )
        return self.get_index(index_name)

    def delete_index(self, index_name):
        self.client.delete_collection(name=index_name)

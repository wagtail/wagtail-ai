from dataclasses import dataclass
from typing import List, Optional

import weaviate

from wagtail_ai.vector_backends import Backend, Index, SearchResponseDocument


@dataclass
class BackendConfig:
    HOST: str
    API_KEY: Optional[str] = None


class WeaviateIndex(Index):
    def __init__(self, index_name: str, api_client: weaviate.Client):
        self.index_name = index_name
        self.client = api_client

    def upsert(self, *, documents):
        with self.client.batch as batch:
            for document in documents:
                batch.add_data_object(
                    document.metadata, self.index_name, vector=document.vector
                )

    def delete(self, *, document_ids: List[str]):
        # TODO: Handle deletion
        raise NotImplementedError

    def similarity_search(self, query_vector, *, limit: int = 5):
        near_vector = {
            "vector": query_vector,
        }
        similar_documents = (
            self.client.query.get(
                self.index_name, ["id", "content_type_id", "object_id", "content"]
            )
            .with_additional("distance")
            .with_near_vector(near_vector)
            .with_limit(limit)
            .do()
        )["data"]["Get"][self.index_name]
        return [
            SearchResponseDocument(id=doc["id"], metadata=doc)
            for doc in similar_documents
        ]


class WeaviateBackend(Backend[BackendConfig, WeaviateIndex]):
    config_class = BackendConfig

    def __init__(self, config):
        super().__init__(config)
        auth_config = weaviate.auth.AuthApiKey(api_key=self.config.API_KEY)
        self.client = weaviate.Client(self.config.HOST, auth_client_secret=auth_config)

    def get_index(self, index_name):
        return WeaviateIndex(index_name, api_client=self.client)

    def create_index(self, index_name, **kwargs):
        self.client.schema.create_class(
            {
                "class": index_name,
            }
        )
        return self.get_index(index_name)

    def delete_index(self, index_name):
        self.client.schema.delete_class(index_name)

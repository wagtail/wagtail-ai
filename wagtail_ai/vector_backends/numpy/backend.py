import logging

from dataclasses import asdict, dataclass
from typing import List

import numpy as np

from wagtail_ai.index import Document, get_vector_indexes
from wagtail_ai.vector_backends import Backend, Index, SearchResponseDocument


logger = logging.Logger(__name__)


@dataclass
class BackendConfig:
    ...


class NumpyIndex(Index):
    def upsert(self, *, documents: List[Document]):
        pass

    def delete(self, *, document_ids: List[str]):
        pass

    def similarity_search(self, query_vector, *, limit: int = 5):
        similarities = []
        vector_index = get_vector_indexes()[self.index_name]
        for document in vector_index.get_documents():
            cosine_similarity = (
                np.dot(query_vector, document.vector)
                / np.linalg.norm(query_vector)
                * np.linalg.norm(document.vector)
            )
            similarities.append((cosine_similarity, document))

        sorted_similarities = sorted(
            similarities, key=lambda pair: pair[0], reverse=True
        )
        top_similarities = [pair[1] for pair in sorted_similarities][:limit]
        return [
            SearchResponseDocument(
                id=similarity.id, metadata=asdict(similarity.metadata)
            )
            for similarity in top_similarities
        ]


class NumpyBackend(Backend[BackendConfig, NumpyIndex]):
    config_class = BackendConfig

    def get_index(self, index_name) -> NumpyIndex:
        return NumpyIndex(index_name)

    def create_index(self, index_name, *, vector_size: int) -> NumpyIndex:
        return self.get_index(index_name)

    def delete_index(self, index_name):
        pass

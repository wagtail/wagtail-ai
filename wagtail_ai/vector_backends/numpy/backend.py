from dataclasses import dataclass
from typing import List

import numpy as np

from wagtail_ai.index import VectorIndex
from wagtail_ai.vector_backends import Backend


@dataclass
class BackendConfig:
    ...


class NumpyBackend(Backend[BackendConfig]):
    config_class = BackendConfig

    def _build_index(self, index_class: None):
        pass

    def search(
        self, index: "VectorIndex", query_embedding, *, limit: int = 5
    ) -> List[dict]:
        similarities = []
        for document in index.get_documents():
            cosine_similarity = (
                np.dot(query_embedding, document.vector)
                / np.linalg.norm(query_embedding)
                * np.linalg.norm(document.vector)
            )
            similarities.append((cosine_similarity, document))

        sorted_similarities = sorted(
            similarities, key=lambda pair: pair[0], reverse=True
        )
        top_similarities = [pair[1] for pair in sorted_similarities][:limit]
        return [
            {
                "id": similarity.id,
                "content_type_id": similarity.metadata.content_type_id,
                "object_id": similarity.metadata.object_id,
            }
            for similarity in top_similarities
        ]

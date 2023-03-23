from typing import List, Optional

import requests


class QdrantClient:
    def __init__(self, *, host: str, api_key: Optional[str]):
        self.host = host
        self.api_key = api_key

    def do_request(self, path: str, method: str, json: Optional[dict] = None) -> dict:
        headers = {}
        if self.api_key:
            headers = {"api-key": self.api_key}

        return requests.request(
            method, f"{self.host}{path}", headers=headers, json=json
        ).json()

    def create_collection(self, *, name: str, vector_size: int):
        self.do_request(
            f"/collections/{name}",
            "PUT",
            {"name": name, "vectors": {"size": vector_size, "distance": "Cosine"}},
        )

    def delete_collection(self, *, name: str):
        self.do_request(f"/collections/{name}", "DELETE")

    def add_point(
        self, *, collection_name: str, id: str, payload: dict, vector: List[float]
    ):
        self.do_request(
            f"/collections/{collection_name}/points",
            "PUT",
            {"id": id, "payload": payload, "vector": vector},
        )

    def search(self, *, collection_name: str, vector: list[float], filter: dict = None):
        return self.do_request(
            f"/collections/{collection_name}/points/search",
            "POST",
            {"vector": vector, "filter": filter},
        )["result"]

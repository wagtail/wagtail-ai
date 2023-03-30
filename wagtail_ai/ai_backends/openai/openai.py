from typing import List, Optional

import requests


BASE_URL = "https://api.openai.com/v1/"


class OpenAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def do_request(self, path: str, json: dict) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        return requests.post(f"{BASE_URL}{path}", headers=headers, json=json).json()

    def chat(
        self, *, system_messages: Optional[List[str]] = None, user_messages: List[str]
    ) -> str:
        system_messages = system_messages if system_messages else []
        all_messages = [
            {"role": "system", "content": message} for message in system_messages
        ] + [{"role": "user", "content": prompt} for prompt in user_messages]

        res = self.do_request(
            "chat/completions",
            {
                "model": "gpt-3.5-turbo",
                "messages": all_messages,
            },
        )
        return res["choices"][0]["message"]["content"]

    def get_embeddings(self, inputs: List[str]) -> List[List[float]]:
        if not inputs:
            return []

        res = self.do_request(
            "embeddings",
            {
                "model": "text-embedding-ada-002",
                "input": inputs,
            },
        )
        return [output["embedding"] for output in res["data"]]

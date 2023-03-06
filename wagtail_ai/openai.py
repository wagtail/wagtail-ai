import requests


BASE_URL = "https://api.openai.com/v1/"


class OpenAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def do_request(self, path: str, json: dict) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        return requests.post(f"{BASE_URL}{path}", headers=headers, json=json).json()

    def chat(self, prompt: str) -> str:
        res = self.do_request(
            "chat/completions",
            {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        print(res)
        return res["choices"][0]["message"]["content"]

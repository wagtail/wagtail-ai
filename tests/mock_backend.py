from typing import List


class MockBackend:
    def prompt(self, prompt: str) -> str:
        return "AI! Don't talk to me about AI!"

    def get_embedding(self, input: str) -> List[float]:
        return [0.1, 0.2, 0.3]

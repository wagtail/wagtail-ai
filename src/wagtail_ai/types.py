from collections.abc import Callable, Iterator
from typing import Any, Protocol


class AIResponse(Protocol):
    """
    Compatible with the llm.Response.
    """

    def __iter__(self) -> Iterator[str]:
        ...

    def text(self) -> str:
        ...


class TextSplitterProtocol(Protocol):
    def __init__(
        self, *, chunk_size: int, length_function: Callable[[str], int], **kwargs: Any
    ) -> None:
        ...

    def split_text(self, text: str) -> list[str]:
        ...


class TextSplitterLengthCalculatorProtocol(Protocol):
    def get_splitter_length(self, text: str) -> int:
        ...

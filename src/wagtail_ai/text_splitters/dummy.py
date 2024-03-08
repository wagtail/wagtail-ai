import logging
from collections.abc import Callable

from ..types import TextSplitterLengthCalculatorProtocol, TextSplitterProtocol

logger = logging.getLogger(__name__)


class DummyTextSplitter(TextSplitterProtocol):
    def __init__(
        self, *, chunk_size: int, length_function: Callable[[str], int]
    ) -> None:
        pass

    def split_text(self, text: str) -> list[str]:
        # Don't do any splitting.
        return [text]


class DummyLengthCalculator(TextSplitterLengthCalculatorProtocol):
    def get_splitter_length(self, text: str) -> int:
        return len(text)

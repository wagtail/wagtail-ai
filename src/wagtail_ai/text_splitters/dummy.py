import logging
from collections.abc import Callable

from ..types import TextSplitterProtocol

logger = logging.getLogger(__name__)


class DummyTextSplitter(TextSplitterProtocol):
    def __init__(
        self, *, chunk_size: int, length_function: Callable[[str], int]
    ) -> None:
        pass

    def split_text(self, text: str) -> str:
        # Don't do any splitting.
        return text

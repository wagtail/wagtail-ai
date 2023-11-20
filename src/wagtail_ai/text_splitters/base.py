from abc import ABCMeta, abstractmethod
from typing import TypeVar

TextSplitterLengthConfig = TypeVar("TextSplitterLengthConfig")


class BaseTextSplitterLength(metaclass=ABCMeta):
    @abstractmethod
    def get_splitter_length(self, text: str) -> int:
        ...

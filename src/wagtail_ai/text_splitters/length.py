import decimal
import logging
import math
import re

from ..types import TextSplitterLengthCalculatorProtocol

logger = logging.getLogger(__name__)


class NaiveTextSplitterCalculator(TextSplitterLengthCalculatorProtocol):
    """
    Text splitter length function that estimates how many tokens there
    are in the text rather than actually giving the correct reading.

    The goal is that we have a safe function that can be used accross
    all the popular models.


    Using OpenAI as a guide:
    - https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them

    - 4 characters is the average length of one token.
    - 3/4 words is the average length of one token.
    """

    characters_per_token: int | float | decimal.Decimal = 4
    words_per_token: int | float | decimal.Decimal = 0.75
    final_multiplier: int | float | decimal.Decimal = 1

    def get_splitter_length(self, text: str) -> int:
        """
        Estimate how many tokens there are in a piece of text.

        """
        word_count = len(re.findall(r"[^\w\s]|\w+", text))
        char_count = len(text)

        # Estimating 1 token per 4 characters.
        token_char_count = math.ceil(char_count / self.characters_per_token)

        # Estimating 1 token per 3/4 words.
        token_word_count = math.ceil(word_count * self.words_per_token)

        logger.debug(
            "Text splitting: token_char_count=%d token_word_count=%d char_count=%d word_count=%d",
            token_char_count,
            token_word_count,
            char_count,
            word_count,
        )

        return math.ceil(
            max(token_char_count, token_word_count) * self.final_multiplier
        )

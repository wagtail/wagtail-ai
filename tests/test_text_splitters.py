import pytest
from test_utils.settings import custom_text_splitting

from wagtail_ai.ai import (
    get_ai_backend,
)
from wagtail_ai.text_splitters.dummy import DummyLengthCalculator, DummyTextSplitter
from wagtail_ai.text_splitters.langchain import LangchainRecursiveCharacterTextSplitter
from wagtail_ai.text_splitters.length import NaiveTextSplitterCalculator


@custom_text_splitting({})
def test_default_text_splitter() -> None:
    ai_backend = get_ai_backend("default")
    text_splitter = ai_backend.get_text_splitter()
    assert isinstance(text_splitter, LangchainRecursiveCharacterTextSplitter)


@custom_text_splitting({})
def test_default_length_calculator() -> None:
    ai_backend = get_ai_backend("default")
    length_calculator = ai_backend.get_splitter_length_calculator()
    assert isinstance(length_calculator, NaiveTextSplitterCalculator)


@custom_text_splitting(
    {"SPLITTER_CLASS": "wagtail_ai.text_splitters.dummy.DummyTextSplitter"}
)
def test_custom_text_splitter() -> None:
    ai_backend = get_ai_backend("default")
    text_splitter = ai_backend.get_text_splitter()
    assert isinstance(text_splitter, DummyTextSplitter)


@custom_text_splitting(
    {
        "SPLITTER_LENGTH_CALCULATOR_CLASS": "wagtail_ai.text_splitters.dummy.DummyLengthCalculator"
    }
)
def test_custom_length_calculator() -> None:
    ai_backend = get_ai_backend("default")
    length_calculator = ai_backend.get_splitter_length_calculator()
    assert isinstance(length_calculator, DummyLengthCalculator)


LENGTH_CALCULATOR_SAMPLE_TEXTS = [
    """Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Morbi ornare magna et urna volutpat, ut fermentum velit tincidunt.
    Aliquam erat volutpat. Nam erat mi, porta eu scelerisque sed, pharetra eget quam.
    Sed aliquet massa purus, vel sagittis libero fermentum nec.
    Donec placerat leo in tortor semper, sit amet venenatis ipsum tincidunt. Fusce at porttitor orci.
    Donec nibh diam, consectetur a sagittis eu, laoreet vitae erat.
    Aliquam bibendum dolor sed ornare aliquet. Aliquam sodales,
    felis nec aliquet condimentum, sem lacus placerat est...""",
    """Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Morbi ornare magna et urna volutpat, ut fermentum velit tincidunt.
    Aliquam erat volutpat. Nam erat mi, porta eu scelerisque sed, pharetra eget quam.
    Sed aliquet massa purus, vel sagittis libero fermentum nec.
    Donec placerat leo in tortor semper, sit amet venenatis ipsum tincidunt. Fusce at porttitor orci.
    Donec nibh diam, consectetur a sagittis eu, laoreet vitae erat.
    Aliquam bibendum dolor sed ornare aliquet. Aliquam sodales,
    felis nec aliquet condimentum, sem lacus placerat est...

    Test.""",
]

NAIVE_LENGTH_CALCULATOR_TESTS_TABLE = [
    (LENGTH_CALCULATOR_SAMPLE_TEXTS[0], 143),
    (LENGTH_CALCULATOR_SAMPLE_TEXTS[1], 146),
]


@pytest.mark.parametrize("test_input,expected", NAIVE_LENGTH_CALCULATOR_TESTS_TABLE)
def test_naive_text_splitter_length_calculator(test_input, expected) -> None:
    length_calculator = NaiveTextSplitterCalculator()
    assert length_calculator.get_splitter_length(test_input) == expected


DUMMY_LENGTH_CALCULATOR_TESTS_TABLE = [
    (val, len(val)) for val in LENGTH_CALCULATOR_SAMPLE_TEXTS
]


@pytest.mark.parametrize("test_input,expected", DUMMY_LENGTH_CALCULATOR_TESTS_TABLE)
def test_dummy_text_splitter_length_calculator(test_input, expected) -> None:
    """
    Dummy length calculator just returns the length of text.
    """
    length_calculator = DummyLengthCalculator()
    assert length_calculator.get_splitter_length(test_input) == expected

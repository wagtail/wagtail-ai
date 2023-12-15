# Text splitting

Sometimes when we send text to an AI model, we need to send more text than the model can process in one go. To do this, we need to split the text you provide in to smaller chunks.

Wagtail AI provides two components that help with this:

- Splitter length calculator - which decides how many characters will fit inside a model's context window based on the `TOKEN_LIMIT` specified in your backend configuration.
- Splitter - which splits your text in to sensible chunks.

## Defaults

By default, Wagtail AI comes with:

 - A naive splitter length calculator that tries to conservatively estimate how many characters will fit without any additional dependencies.
 - A recursive text splitter vendored from Langchain that tries to split on paragraphs, then new lines, then spaces.

## Customization

You may wish to create your own splitters or length calculators. To do this, you can override the default classes with your own as follows:

```python
WAGTAIL_AI = {
    "BACKENDS": {
        "default": {
            "CLASS": "wagtail_ai.ai.llm.LLMBackend",
            "CONFIG": {
                "MODEL_ID": "gpt-3.5-turbo",
            },
            "TEXT_SPLITTING": {
                "SPLITTER_CLASS": "path.to.your.custom.SplitterClass",
                "SPLITTER_LENGTH_CALCULATOR_CLASS": "path.to.your.custom.SplitterLengthCalculatorClass",
            },
        }
    }
}
```

### Custom text splitter

The spliter class must implement the [`TextSplitterProtocol`](https://github.com/wagtail/wagtail-ai/blob/main/src/wagtail_ai/types.py).

For example, if you wanted to use a different splitter from Langchain:

```python
from collections.abc import Callable, Iterator
from typing import Any

from langchain.text_splitter import (
    HTMLHeaderTextSplitter as LangchainHTMLHeaderTextSplitter,
)

from wagtail_ai.types import TextSplitterProtocol


class HTMLHeaderTextSplitter(TextSplitterProtocol):
    def __init__(
        self, *, chunk_size: int, length_function: Callable[[str], int], **kwargs: Any
    ) -> None:
        self.splitter = LangchainHTMLHeaderTextSplitter(
            chunk_size=chunk_size,
            length_function=length_function,
        )

    def split_text(self, text: str) -> list[str]:
        return self.splitter.split_text(text)
```

### Custom splitter length calculator class

You may want to implement a custom length calculator to get a more accurate length estimate for your chosen model.

The spliter length class must implement the [`TextSplitterLengthCalculatorProtocol`](https://github.com/wagtail/wagtail-ai/blob/main/src/wagtail_ai/types.py).

For example, using [tiktoken](https://github.com/openai/tiktoken) for OpenAI models.:

```python
import tiktoken

from wagtail_ai.types import TextSplitterLengthCalculatorProtocol


class GPT35TurboLengthCalculator(TextSplitterLengthCalculatorProtocol):
    MODEL_ID = "chatgpt-3.5-turbo"

    def get_splitter_length(self, text: str) -> int:
        encoding = tiktoken.encoding_for_model(self.MODEL_ID)
        return len(encoding.encode(text))
```

## Further reading

- [OpenAI token limits](https://platform.openai.com/docs/models)
- [Langchain's Recursive text splitter](https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/recursive_text_splitter)
- [tiktoken](https://github.com/openai/tiktoken)

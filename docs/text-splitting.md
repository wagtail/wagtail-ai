# Text splitting

Using chat models requires splitting the text into smaller chunks that the model can process.

There are two components to this:

- Splitter length calculator
- Splitter

The splitter needs the length calculator to know when to split for each different chat model.

This can be controlled with the `TOKEN_LIMIT` in the backend configuration.

## Defaults

By default, Wagtail AI comes with:

 - Langchain `RecursiveCharacterTextSplitter` class that is vendored in Wagtail AI.
 - A naive splitter length calculator that does not actually do a proper text splitting,
   only estimates how many tokens there are in the supplied text.

By default Wagtail AI does not require you to use any third-party dependencies to
achieve the text splitting required for most chat models. That's why we've vendored
the Langchain splitter so it avoids relying on big external packages for a single task.

In the future development of Wagtail AI we might add support for more precise
optional backends in addition to the default ones.

## Customization

Wagtail AI allows you to customize the splitter and the splitter length calculator logic
for each backend so that then you can tailor them to the specific chat model you want to use.

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

The spliter class must implement the `TextSplitterProtocol`
([source](https://github.com/wagtail/wagtail-ai/blob/main/src/wagtail_ai/types.py)).


E.g. if you wanted to use the actual Langchain dependency, you could specify
a custom class like this:

```python
from collections.abc import Callable, Iterator
from typing import Any

from langchain.text_splitter import RecursiveCharacterTextSplitter

from wagtail_ai.types import TextSplitterProtocol


class RecursiveCharacterTextSplitter(TextSplitterProtocol):
    def __init__(
        self, *, chunk_size: int, length_function: Callable[[str], int], **kwargs: Any
    ) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            length_function=length_function,
            keep_separator=kwargs.get("keep_separator", True),
        )

    def split_text(self, text: str) -> list[str]:
        return self.splitter.split_text(text)
```

### Custom splitter length calculator class

Each chat model comes with their own tokenizing logic. You would have to implement
a custom splitter for each model that you want to use if you want to use a more
precise length calculator, e.g. [tiktoken](https://github.com/openai/tiktoken)
for OpenAI models.

E.g. a custom calculator for the ChatGPT 3.5 Turbo chat model that uses
the proper tokenizer.

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

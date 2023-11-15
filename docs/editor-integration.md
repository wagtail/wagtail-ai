# Editor Integration

Wagtail AI integrates with Wagtail's Draftail rich text editor to provide tools to help write content.

By default, it includes tools to:

* Run AI assisted spelling/grammar checks on your content
* Generate additional content based on what you're writing

You can also define your own prompts:

### Adding Your Own Prompts

To add custom prompts, add the `WAGTAIL_AI_PROMPTS` setting to your settings file. This is a list of all the prompts to enable, where each prompt is a dictionary in the form:

```python
{
    "label": "Short Label",
    "description": "More complete description",
    "prompt": "The prompt to be sent before your text to the OpenAI API",
    "method": "replace/append",
}
```

where `method` is either:

* `replace` if the AI response should replace the text
* `append` if the response should be appended to the end of the existing text

e.g. to extend the default prompts with your own, add:

```python
import wagtail_ai

WAGTAIL_AI_PROMPTS = wagtail_ai.DEFAULT_PROMPTS + [
    {
        "label": "Simplify",
        "description": "Rewrite your text in a simpler form",
        "prompt": "Rewrite the following text to make it simpler and more succinct",
        "method": "replace",
    }
]
```

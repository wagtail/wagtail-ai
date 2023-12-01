# Editor Integration

Wagtail AI integrates with Wagtail's Draftail rich text editor to provide tools to help write content.

By default, it includes tools to:

* Run AI assisted spelling/grammar checks on your content
* Generate additional content based on what you're writing

You can also define your own prompts:

### Adding Your Own Prompts

Explore the [ModelViewSet](https://docs.wagtail.org/en/stable/reference/viewsets.html#modelviewset) labeled `Prompts` within the Wagtail settings menu, here you'll be able to view, edit and add new prompts.


To customize the default prompts offered by Wagtail AI, introduce the `WAGTAIL_AI_PROMPTS` setting in your settings file. This setting is a list containing all the prompts loaded during the initial app migration `0002_populate_default_prompts`. Each prompt is represented as a dictionary in the following format:

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

# Rich text editor integration

Wagtail AI integrates with Wagtail's Draftail rich text editor to provide tools to help write content. To use it, highlight some text and click the 'magic wand' icon in the toolbar.

By default, it includes prompts that:

* Run AI assisted spelling/grammar checks on your content
* Generate additional content based on what you're writing

!!! note

    This is a legacy feature and kept for backwards compatibility. In the future, we will use [AI Providers](./ai-providers.md) (instead of backends) to build agent-based features using [django-ai-core](https://github.com/wagtail/django-ai-core).

### Adding Your Own Prompts

You can add your own prompts and customise existing prompts from the Wagtail admin under Settings -> Prompts.

When creating prompts you can provide a label and description to help describe the prompt to your editors, specify the full prompt that will be passed with your text to the AI, and a 'method', which can be one of:

- 'Append after existing content' - keep your existing content intact and add the response from the AI to the end (useful for completions/suggestions).
- 'Replace content' - replace the content in the editor with the response from the AI (useful for corrections, rewrites and translations.)

### Configuring the AI backend

By default, the `"default"` model will be used for text operations in the editor. To use a different model, set `TEXT_COMPLETION_BACKEND` to the name of another backend:

```python
WAGTAIL_AI = {
    "BACKENDS": {
        "gpt4": {
            "CLASS": "wagtail_ai.ai.openai.OpenAIBackend",
            "CONFIG": {
                "MODEL_ID": "gpt-4",
            },
        },
    },
    "TEXT_COMPLETION_BACKEND": "gpt4",
}
```

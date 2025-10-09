# Content feedback

Wagtail AI can provide qualitative feedback on your page content, helping editors improve quality and readability. This feature analyzes your content and provides actionable suggestions for improvement.

## Overview

The content feedback feature adds a new section to the "Checks" side panel in the page editor that displays:

- **Quality score**: A numerical rating (1-3) indicating content quality
- **Overall feedback**: General strengths and observations about the content
- **Specific improvements**: Actionable suggestions with explanation

Content feedback is automatically available in the page editor when Wagtail AI is installed and configured.

## How it works

When an editor requests feedback:

1. The page content is sent to the configured AI provider
2. The AI analyzes the content for quality and adherence to any custom criteria
3. Feedback is returned in a structured format with:
   - A quality score (1 = needs major improvement, 2 = adequate, 3 = excellent)
   - Qualitative observations about strengths
   - Specific improvement suggestions with an explanation

## Configuring

You can configure the prompt used by the feature by going to **Settings → Agent** in the admin and set the following fields:

### Content type

- **Plain text**: Sends text-only version of the content
- **HTML**: Sends the full HTML, useful for analyzing structure (default)

### Prompt

Add additional instructions to adjust the feedback given by the agent by filling in the prompt field. For example:

```
Content must include the word 'sustainability'.
The tone should be professional and academic.
Paragraphs should be no longer than 3 sentences.
```

When set, the AI will consider these custom criteria in addition to general quality assessments.

## Customization

If you wish to customize how the content feedback agent works, you can subclass the `ContentFeedbackAgent` and override methods and properties as needed. The subclass can be registered with django-ai-core's `registry` to replace wagtail-ai's built in agent. For example, to change the provider used:

```python
from django_ai_core.contrib.agents import registry
from wagtail_ai.agents.content_feedback import ContentFeedbackAgent


@registry.register()
class CustomContentFeedbackAgent(ContentFeedbackAgent):
    provider_alias = "custom_provider"
```

The AI must return the result in this structure:

```json
{
  "quality_score": 2,
  "qualitative_feedback": [
    "Clear and informative structure",
    "Good use of examples to illustrate points",
    "Some sentences could be more concise"
  ],
  "specific_improvements": [
    {
      "original_text": "The system that we use for processing is very efficient and fast",
      "suggested_text": "Our processing system is efficient and fast",
      "explanation": "More concise phrasing improves readability"
    }
  ]
}
```

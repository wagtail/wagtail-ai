# Field panel integration

Wagtail AI provides AI-powered field panels that add the ability to generate suggestions for page titles and descriptions.

## `AITitleFieldPanel`

The `AITitleFieldPanel` extends Wagtail's `TitleFieldPanel` to provide AI-powered page title suggestions based on your page's content.

```python
from wagtail.models import Page
from wagtail_ai.panels import AITitleFieldPanel


class BlogPage(Page):
    # Your page fields...

    content_panels = [
        AITitleFieldPanel("title"),
        # Other panels...
    ]
```

## `AIDescriptionFieldPanel`

The `AIDescriptionFieldPanel` provides AI-powered meta description suggestions by summarizing your page content.

```python
from wagtail.models import Page
from wagtail_ai.panels import AIDescriptionFieldPanel


class BlogPage(Page):
    promote_panels = [
        # ...
        AIDescriptionFieldPanel("search_description"),
    ]
```

## Enabling `AITitleFieldPanel` and `AIDescriptionFieldPanel` on all page models

To enable the AI-powered title and description panels on all your page models by default, you can override the default `content_panels` and `promote_panels` of the base page model:

```python
from wagtail.models import Page
from wagtail_ai.panels import AITitleFieldPanel, AIDescriptionFieldPanel

Page.content_panels = [AITitleFieldPanel("title")]
Page.promote_panels = [
    MultiFieldPanel(
        [
            "slug",
            "seo_title",
            # Enable AI prompt on the search_description field
            AIDescriptionFieldPanel("search_description"),
        ],
        heading="For search engines",
    ),
    MultiFieldPanel(["show_in_menus"], heading="For site menus"),
]
```

## Customizing prompts

The prompts for title generation can be customized in **Settings → Agent** in the Wagtail admin under "Page metadata". The following placeholder tokens are available to use in the prompts:

- `{content_html}`: The HTML content of the page
- `{content_text}`: The plain text content of the page
- `{max_length}`: The maximum length (in characters) set on the input widget
- `{input}`: The current value of the input widget

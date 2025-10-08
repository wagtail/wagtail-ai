from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

from wagtail_ai.panels import AIDescriptionFieldPanel, AITitleFieldPanel

# Replace the default TitleFieldPanel with an AITitleFieldPanel.
Page.content_panels[0] = AITitleFieldPanel("title", classname="title")  # type: ignore
# Replace the default `search_description` FieldPanel with an AIFieldPanel.
Page.promote_panels[0].args[0][-1] = AIDescriptionFieldPanel("search_description")  # type: ignore


class ExamplePage(Page):
    body = RichTextField()

    content_panels = [*Page.content_panels, FieldPanel("body")]

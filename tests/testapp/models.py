from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

from wagtail_ai.panels import AIFieldPanel, AITitleFieldPanel
from wagtail_ai.prompts import DefaultPrompt

# Replace the default TitleFieldPanel with an AITitleFieldPanel.
Page.content_panels[0] = AITitleFieldPanel("title", classname="title")  # type: ignore
description_panel = AIFieldPanel(
    "search_description",
    prompts=[DefaultPrompt.DESCRIPTION],
)
# Replace the default `search_description` FieldPanel with an AIFieldPanel.
if WAGTAIL_VERSION >= (6, 4):  # type: ignore
    Page.promote_panels[0].args[0][-1] = description_panel  # type: ignore
else:
    Page.promote_panels[0].children[-1] = description_panel  # type: ignore


class ExamplePage(Page):
    body = RichTextField()

    content_panels = [*Page.content_panels, FieldPanel("body")]

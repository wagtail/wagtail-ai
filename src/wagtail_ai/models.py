import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting
from wagtail.search import index

from wagtail_ai.prompts import DEFAULT_PROMPTS


class Prompt(models.Model, index.Indexed):
    class Method(models.TextChoices):
        REPLACE = "replace", _("Replace content")
        APPEND = "append", _("Append after existing content")

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    default_prompt_id = models.SmallIntegerField(unique=True, editable=False, null=True)
    label = models.CharField(max_length=50)
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "The prompt description, displayed alongside its label on the settings listing."
        ),
    )
    prompt = models.TextField(  # noqa: DJ001
        null=True,  # field is nullable to manage default prompts, see the prompt_value property for more info.
        blank=False,
        help_text=_(
            "The prompt text sent to the Large Language Model (e.g. ChatGPT) to generate content."
        ),
    )
    method = models.CharField(
        max_length=25,
        choices=Method.choices,
        help_text=_("The method used for processing the responses to the prompt."),
    )

    search_fields = [
        index.AutocompleteField("label"),
        index.SearchField("description"),
        index.SearchField("prompt"),
    ]

    def __str__(self):
        return self.label

    def get_default_prompt_value(self) -> str:
        """
        Return the default prompt value from DEFAULT_PROMPTS.
        """
        return next(
            (
                prompt["prompt"]
                for prompt in DEFAULT_PROMPTS
                if prompt["default_prompt_id"] == self.default_prompt_id
            ),
            "",
        )

    @property
    def is_default(self) -> bool:
        """
        Returns True if the prompt is one of the default prompts.
        """
        return self.default_prompt_id is not None

    @property
    def prompt_value(self) -> str:
        """
        Return the prompt value, otherwise if the prompt is None and belongs
        to the default prompts, map to the default prompt value.
        """
        if not self.prompt:
            if self.is_default:
                return self.get_default_prompt_value()
            else:
                raise ValueError("Prompt value is empty and not a default prompt.")
        return self.prompt


class AgentPromptDefaults:
    @classmethod
    def page_title_prompt(cls):
        return (
            "Create an SEO-friendly page title, and respond ONLY with the title "
            "in plain text (without quotes), for the following "
            "web page content:\n\n"
            "{content_html}"
        )

    @classmethod
    def page_description_prompt(cls):
        return (
            "Create an SEO-friendly meta description, and respond ONLY with the "
            "description in plain text (without quotes) for the following web page "
            "content:\n\n"
            "{content_html}"
        )

    @classmethod
    def image_title_prompt(cls):
        return (
            "Generate a title (in plain text, no longer than "
            "{max_length} characters, without quotes) for the following image: {image}"
        )

    @classmethod
    def image_description_prompt(cls):
        return (
            "Generate a description (in plain text, no longer than "
            "{max_length} characters) for the following image: {image}"
        )

    @classmethod
    def contextual_alt_text_prompt(cls):
        return """Generate an alt text (and only the text) for the following image:
{image}

Make the alt text relevant to the following content shown before the image:

---
{form_context_before}
---

and also relevant to the following content shown after the image:

---
{form_context_after}
---"""


class AgentSettingsMixin(models.Model):
    class ContentFeedbackContentType(models.TextChoices):
        TEXT = "text", _("Plain text")
        HTML = "html", _("HTML")

    page_title_prompt = models.TextField(
        blank=True,
        default=AgentPromptDefaults.page_title_prompt,
    )
    page_description_prompt = models.TextField(
        blank=True,
        default=AgentPromptDefaults.page_description_prompt,
    )
    image_title_prompt = models.TextField(
        blank=True,
        default=AgentPromptDefaults.image_title_prompt,
    )
    image_description_prompt = models.TextField(
        blank=True,
        default=AgentPromptDefaults.image_description_prompt,
    )
    contextual_alt_text_prompt = models.TextField(
        blank=True,
        default=AgentPromptDefaults.contextual_alt_text_prompt,
    )
    content_feedback_prompt = models.TextField(blank=True)
    content_feedback_content_type = models.CharField(
        max_length=64,
        choices=ContentFeedbackContentType.choices,
        default=ContentFeedbackContentType.HTML,
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel(
                    "page_title_prompt",
                    heading=_("Page title prompt"),
                    help_text=_("Prompt to use for generating page titles."),
                ),
                FieldPanel(
                    "page_description_prompt",
                    heading=_("Page description prompt"),
                    help_text=_("Prompt to use for generating page descriptions."),
                ),
            ],
            heading=_("Page metadata"),
        ),
        MultiFieldPanel(
            [
                FieldPanel(
                    "image_title_prompt",
                    heading=_("Image title prompt"),
                    help_text=_(
                        "Prompt to use for generating image titles when uploading or "
                        "editing an image."
                    ),
                ),
                FieldPanel(
                    "image_description_prompt",
                    heading=_("Image description prompt"),
                    help_text=_(
                        "Prompt to use for generating image descriptions when "
                        "uploading or editing an image."
                    ),
                ),
                FieldPanel(
                    "contextual_alt_text_prompt",
                    heading=_("Contextual alt text prompt"),
                    help_text=_(
                        "Prompt to use for generating contextual image alt text "
                        "in the page editor."
                    ),
                ),
            ],
            heading=_("Images"),
        ),
        MultiFieldPanel(
            [
                FieldPanel(
                    "content_feedback_content_type",
                    heading=_("Content type"),
                    help_text=_("The format of the content to review."),
                ),
                FieldPanel(
                    "content_feedback_prompt",
                    heading=_("Prompt"),
                    help_text=_(
                        "Additional instructions to adjust the feedback given "
                        "by the agent."
                    ),
                ),
            ],
            heading=_("Content feedback"),
        ),
    ]

    class Meta:  # type: ignore
        abstract = True
        verbose_name = _("Agents")

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)
        # Ensure these prompts have a value, falling back to defaults if needed.
        for field_name in [
            "page_title_prompt",
            "page_description_prompt",
            "image_title_prompt",
            "image_description_prompt",
            "contextual_alt_text_prompt",
        ]:
            field_value = getattr(self, field_name)
            if not field_value:
                setattr(self, field_name, getattr(AgentPromptDefaults, field_name)())


class AgentSettings(AgentSettingsMixin, BaseGenericSetting):
    class Meta(AgentSettingsMixin.Meta):  # type: ignore
        abstract = False

    def __str__(self):
        return str(self._meta.verbose_name)

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


class AgentSettingsMixin(models.Model):
    class ContentFeedbackContentType(models.TextChoices):
        TEXT = "text", _("Plain text")
        HTML = "html", _("HTML")

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


class AgentSettings(AgentSettingsMixin, BaseGenericSetting):
    class Meta(AgentSettingsMixin.Meta):  # type: ignore
        abstract = False

    def __str__(self):
        return str(self._meta.verbose_name)

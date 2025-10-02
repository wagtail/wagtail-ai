import json
from enum import IntEnum

from django_ai_core.contrib.agents import Agent, AgentParameter, registry
from pydantic import BaseModel, Field

from .base import get_agent_settings, get_llm_service


class QualityScore(IntEnum):
    NEEDS_MAJOR_IMPROVEMENT = 1
    ADEQUATE = 2
    EXCELLENT = 3


class SpecificImprovement(BaseModel):
    original_text: str = Field(description="The original text that needs improvement")
    suggested_text: str = Field(
        description="The suggested revised text in the content's language"
    )
    explanation: str = Field(
        description=(
            "A brief explanation in the editor's language for why this change "
            "would improve the content"
        )
    )


class ContentFeedbackSchema(BaseModel):
    quality_score: QualityScore = Field(
        description=(
            "Quality score between 1 and 3 "
            "(1=needs major improvement, 2=adequate, 3=excellent)"
        ),
    )
    qualitative_feedback: list[str] = Field(
        description=(
            "3-5 bullet points of qualitative feedback highlighting strengths "
            "and areas for improvement"
        ),
        min_length=3,
        max_length=5,
    )
    specific_improvements: list[SpecificImprovement] = Field(
        description=(
            "Specific text improvements with original text, suggested revised text, "
            "and a brief explanation for why each change would improve the content"
        ),
        min_length=1,
    )


@registry.register()
class ContentFeedbackAgent(Agent):
    slug = "wai_content_feedback"
    description = "An agent that provides feedback on content quality."
    parameters = [
        AgentParameter(
            name="content_text",
            type=str,
            description="The text content to review",
        ),
        AgentParameter(
            name="content_html",
            type=str,
            description="The HTML content to review",
        ),
        AgentParameter(
            name="content_language",
            type=str,
            description="The language of the content (e.g. 'American English')",
        ),
        AgentParameter(
            name="editor_language",
            type=str,
            description=(
                "The preferred language for the editor interface (e.g. 'French')"
            ),
        ),
    ]
    _response_format = ContentFeedbackSchema

    def execute(
        self,
        content_text: str,
        content_html: str,
        content_language: str,
        editor_language: str,
    ) -> dict:
        settings = get_agent_settings()
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that responds with structured data according to the provided schema. The language rules specified are IMPORTANT. Always ensure the feedback and improvements are in the correct language.",
            },
            {
                "role": "system",
                "content": f"""Analyze the given content and provide:
1. A quality score between 1 and 3 (1=needs major improvement, 2=adequate, 3=excellent)
2. 3-5 bullet points of qualitative feedback highlighting strengths and areas for improvement in {editor_language}
3. Specific text improvements with original text, suggested revised text in {content_language}, and a brief explanation
   in {editor_language} for why each change would improve the content

The language rules specified are IMPORTANT. Always ensure the feedback and improvements are in the correct language.

Return JSON with the provided structure WITHOUT the markdown code block. Start immediately with a {{ character and end with a }} character.""",
            },
        ]

        messages += self._get_prompt_messages(settings)

        match settings.content_feedback_content_type:
            case settings.ContentFeedbackContentType.TEXT:
                content = content_text
            case settings.ContentFeedbackContentType.HTML | _:
                content = content_html

        messages.append(
            {
                "role": "system",
                "content": f"Content to review:\n\n{content}",
            }
        )

        return self._get_result(messages)

    def _get_prompt_messages(self, settings) -> list[dict]:
        messages = []
        if settings.content_feedback_prompt:
            messages.append(
                {
                    "role": "user",
                    "content": settings.content_feedback_prompt,
                }
            )
        return messages

    def _get_result(self, messages: list[dict]) -> dict:
        client = get_llm_service()
        result = client.completion(
            messages=messages,
            response_format=self._response_format,
        )
        return json.loads(result.choices[0].message.content)  # type: ignore

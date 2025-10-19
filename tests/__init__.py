"""
Tests package initialization.

This module registers the agents with django_ai_core on import, which is required
for URL resolution to work since it depends on getting registered agents. Here we
trigger the registration by importing the agents directly.
"""

from wagtail_ai.agents import ContentFeedbackAgent, SuggestedContentAgent
from wagtail_ai.agents.basic_prompt import BasicPromptAgent  # noqa

__all__ = ["ContentFeedbackAgent", "SuggestedContentAgent", "BasicPromptAgent"]
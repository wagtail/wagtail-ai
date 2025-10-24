"""Agents package exports.

Avoid importing submodules here to prevent import-time side effects that
require Django/Wagtail apps to be loaded. Callers should import specific
submodules (for example ``from wagtail_ai.agents.base import get_llm_service``)
so that imports happen at the point they are needed.
"""

from .base import get_llm_service
from .content_feedback import ContentFeedbackAgent
from .suggested_content import SuggestedContentAgent

__all__ = ["ContentFeedbackAgent", "SuggestedContentAgent", "get_llm_service"]

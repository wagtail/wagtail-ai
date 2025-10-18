from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ImproperlyConfigured

from wagtail_ai.agents.base import get_llm_service, get_provider


class TestGetProvider:
    def test_returns_provider_by_alias(self, settings) -> None:
        """Return provider by alias."""
        settings.WAGTAIL_AI = {
            "PROVIDERS": {
                "default": {"provider": "openai", "model": "gpt-4o-mini"},
                "premium": {"provider": "anthropic", "model": "claude-3-5-sonnet"},
            }
        }
        provider = get_provider("premium")
        assert provider == {"provider": "anthropic", "model": "claude-3-5-sonnet"}

    def test_returns_default_provider_when_alias_not_explicit(self, settings) -> None:
        settings.WAGTAIL_AI = {
            "PROVIDERS": {
                "default": {"provider": "openai", "model": "gpt-4o-mini"},
            }
        }
        provider = get_provider()
        assert provider == {"provider": "openai", "model": "gpt-4o-mini"}

    def test_raises_error_when_alias_not_found(self, settings) -> None:
        settings.WAGTAIL_AI = {
            "PROVIDERS": {
                "default": {"provider": "openai", "model": "gpt-4o-mini"},
            }
        }
        with pytest.raises(ImproperlyConfigured) as exc_info:
            get_provider("premium")
        assert "Provider with alias 'premium' not found" in str(exc_info.value)

    def test_legacy_fallback_for_default_provider(self, settings) -> None:
        """Test the deprecated fallback behavior when default provider not configured."""
        settings.WAGTAIL_AI = {
            "BACKENDS": {
                "default": {
                    "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                    "CONFIG": {"MODEL_ID": "echo-model"},
                }
            }
        }

        with patch("wagtail_ai.agents.base.ai.get_backend") as mock_get_backend:
            mock_backend = MagicMock()
            mock_backend.config.model_id = "echo-model"
            mock_get_backend.return_value = mock_backend

            with pytest.warns(match="No 'default' provider configured.*deprecated"):
                provider = get_provider("default")

            assert provider == {"provider": "openai", "model": "echo-model"}

    def test_provider_with_extra_config(self, settings) -> None:
        """Test that extra configuration keys are preserved."""
        settings.WAGTAIL_AI = {
            "PROVIDERS": {
                "default": {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "api_base": "https://api.example.com",
                }
            }
        }
        provider = get_provider("default")
        assert provider == {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "api_base": "https://api.example.com",
        }


class TestGetLLMService:
    def test_returns_llm_service_for_default_provider(self, settings) -> None:
        """LLM service is created for default provider."""
        settings.WAGTAIL_AI = {
            "PROVIDERS": {
                "default": {"provider": "openai", "model": "gpt-4o-mini"},
            }
        }

        with patch("wagtail_ai.agents.base.LLMService.create") as mock_create:
            mock_service = MagicMock()
            mock_create.return_value = mock_service

            service = get_llm_service()

            mock_create.assert_called_once_with(provider="openai", model="gpt-4o-mini")
            assert service == mock_service

    def test_returns_llm_service_for_specific_alias(self, settings) -> None:
        settings.WAGTAIL_AI = {
            "PROVIDERS": {
                "default": {"provider": "openai", "model": "gpt-4o-mini"},
                "premium": {"provider": "anthropic", "model": "claude-3-5-sonnet"},
            }
        }

        with patch("wagtail_ai.agents.base.LLMService.create") as mock_create:
            mock_service = MagicMock()
            mock_create.return_value = mock_service

            service = get_llm_service("premium")

            mock_create.assert_called_once_with(
                provider="anthropic", model="claude-3-5-sonnet"
            )
            assert service == mock_service

    def test_caches_service_for_same_alias(self, settings) -> None:
        settings.WAGTAIL_AI = {
            "PROVIDERS": {
                "default": {"provider": "openai", "model": "gpt-4o-mini"},
            }
        }

        with patch("wagtail_ai.agents.base.LLMService.create") as mock_create:
            mock_service = MagicMock()
            mock_create.return_value = mock_service

            # Call twice with same alias
            service1 = get_llm_service("default")
            service2 = get_llm_service("default")

            # Should only create once due to caching
            mock_create.assert_called_once()
            assert service1 is service2

    def test_creates_different_services_for_different_aliases(self, settings) -> None:
        settings.WAGTAIL_AI = {
            "PROVIDERS": {
                "default": {"provider": "openai", "model": "gpt-4o-mini"},
                "premium": {"provider": "anthropic", "model": "claude-3-5-sonnet"},
            }
        }

        with patch("wagtail_ai.agents.base.LLMService.create") as mock_create:
            mock_service1 = MagicMock()
            mock_service2 = MagicMock()
            mock_create.side_effect = [mock_service1, mock_service2]

            service1 = get_llm_service("default")
            service2 = get_llm_service("premium")

            assert mock_create.call_count == 2
            assert service1 is not service2

    def test_raises_error_when_provider_not_found(self, settings) -> None:
        settings.WAGTAIL_AI = {
            "PROVIDERS": {
                "default": {"provider": "openai", "model": "gpt-4o-mini"},
            }
        }

        with pytest.raises(ImproperlyConfigured):
            get_llm_service("nonexistent")

    def test_passes_extra_config_to_llm_service(self, settings) -> None:
        settings.WAGTAIL_AI = {
            "PROVIDERS": {
                "default": {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "api_base": "https://api.example.com",
                }
            }
        }

        with patch("wagtail_ai.agents.base.LLMService.create") as mock_create:
            mock_service = MagicMock()
            mock_create.return_value = mock_service

            get_llm_service()

            mock_create.assert_called_once_with(
                provider="openai",
                model="gpt-4o-mini",
                api_base="https://api.example.com",
            )

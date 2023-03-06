from django.conf import settings
from django.exceptions import ImproperlyConfigured


try:
    settings.OPENAI_API_KEY
except AttributeError:
    raise ImproperlyConfigured(
        "The OPENAI_API_KEY setting must be configured to use Wagtail AI"
    )

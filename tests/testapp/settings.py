"""
Django settings for temp project.

For more information on this file, see
https://docs.djangoproject.com/en/stable/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/stable/ref/settings/
"""

import os

import dj_database_url

# Build paths inside the project like this: os.path.join(PROJECT_DIR, ...)
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/stable/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "c6u0-9c!7nilj_ysatsda0(f@e_2mws2f!6m0n^o*4#*q#kzp)"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "wagtail_ai",
    "testapp",
    "wagtail.contrib.search_promotions",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.embeds",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.api.v2",
    "wagtail.contrib.routable_page",
    "wagtail.contrib.styleguide",
    "wagtail.sites",
    "wagtail",
    "taggit",
    "rest_framework",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "testapp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]


# Using DatabaseCache to make sure that the cache is cleared between tests.
# This prevents false-positives in some wagtail core tests where we are
# changing the 'wagtail_root_paths' key which may cause future tests to fail.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache",
    }
}


# don't use the intentionally slow default password hasher
PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)


# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(default="sqlite:///test_wagtail_ai.db"),
}


# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": os.environ.get(
            "STATICFILES_STORAGE",
            "django.contrib.staticfiles.storage.StaticFilesStorage",
        ),
    },
}

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = []

STATIC_ROOT = os.environ.get("STATIC_ROOT", os.path.join(BASE_DIR, "test-static"))
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "test-media")


# Wagtail settings

WAGTAIL_SITE_NAME = "Wagtail AI test site"

if os.environ.get("WAGTAIL_AI_DEFAULT_BACKEND") == "chatgpt":
    WAGTAIL_AI = {
        "BACKENDS": {
            "default": {
                "CLASS": "wagtail_ai.ai.llm.LLMBackend",
                "CONFIG": {
                    "MODEL_ID": "gpt-4.1-mini",
                },
            },
            "vision": {
                "CLASS": "wagtail_ai.ai.openai.OpenAIBackend",
                "CONFIG": {
                    "MODEL_ID": "gpt-4.1-mini",
                    "TOKEN_LIMIT": 300,
                },
            },
        },
        "PROVIDERS": {
            "default": {
                "provider": "openai",
                "model": "gpt-4.1-mini",
            },
        },
        "IMAGE_DESCRIPTION_BACKEND": "vision",
    }

else:
    WAGTAIL_AI = {
        "BACKENDS": {
            "default": {
                "CLASS": "wagtail_ai.ai.echo.EchoBackend",
                "CONFIG": {
                    "MODEL_ID": "echo",
                    "MAX_WORD_SLEEP_SECONDS": 1,
                    "TOKEN_LIMIT": 100,
                },
            },
        },
        "PROVIDERS": {
            "default": {
                "provider": "foo",
                "model": "bar",
            },
        },
        "IMAGE_DESCRIPTION_BACKEND": "default",
    }

WAGTAILIMAGES_IMAGE_FORM_BASE = "wagtail_ai.forms.DescribeImageForm"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s][%(process)d][%(levelname)s][%(name)s] %(message)s"
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "wagtail_ai": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "llm": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "testapp": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

FORMS_URLFIELD_ASSUME_HTTPS = True

WAGTAILADMIN_BASE_URL = "http://testserver"

# django-ai-core settings
DJANGO_AI_CORE = {
    'INDEXES': {
        'default': {
            'BACKEND': 'django_ai_core.contrib.index.backends.dummy.DummyIndex',
            'CONFIG': {},
        },
    },
    'PROVIDERS': {
        'default': {
            'BACKEND': 'django_ai_core.contrib.llm.backends.dummy.DummyLLMBackend',
            'CONFIG': {},
        },
    },
}

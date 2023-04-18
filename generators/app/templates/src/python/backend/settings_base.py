import io
import os
from urllib.parse import urlparse

import environ
from google.cloud import secretmanager

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# On AppEngine this env variable should be set, locally this should be set in .envrc
GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")


_env_file = os.path.join(PROJECT_DIR, ".env")
_env = environ.Env(
    DEBUG=(bool, False),
    USE_CLOUD_SQL_AUTH_PROXY=(bool, False),
)

if os.path.isfile(_env_file):
    # Use a local secret file, if provided
    _env.read_env(_env_file, interpolate=True)

elif GOOGLE_CLOUD_PROJECT:
    # Pull secrets from Secret Manager
    _env.read_env(
        io.StringIO(
            secretmanager.SecretManagerServiceClient()
            .access_secret_version(
                name="projects/{0}/secrets/{1}/versions/latest".format(
                    GOOGLE_CLOUD_PROJECT,
                    os.environ.get("SETTINGS_NAME", "backend_settings"),
                ),
            )
            .payload.data.decode("UTF-8")
        )
    )

else:
    raise Exception("No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found.")


REMOTE_ENVIRONMENT = "GAE_ENV" in os.environ and os.environ["GAE_ENV"] == "standard"
SECRET_KEY = _env("SECRET_KEY")
DEBUG = _env("DEBUG")
WSGI_APPLICATION = "backend.wsgi.application"

# SECURITY WARNING: It's recommended that you use this when
# running in production. The URL will be known once you first deploy
# to App Engine. This code takes the URL and converts it to both these settings formats.
if not DEBUG:
    APPENGINE_URL = _env("APPENGINE_URL")

    # Ensure a scheme is present in the URL before it's processed.
    if not urlparse(APPENGINE_URL).scheme:
        APPENGINE_URL = f"https://{APPENGINE_URL}"

    ALLOWED_HOSTS = [urlparse(APPENGINE_URL).netloc]
    CSRF_TRUSTED_ORIGINS = [APPENGINE_URL]
    SECURE_SSL_REDIRECT = True
else:
    ALLOWED_HOSTS = ["*"]


# DATABASE

# Use empty configuration as a placeholder. Database connections should be
# defined in the remote base settings, individual service settings and dev
# settings
DATABASES = {"default": _env.db()}

# Wrap all view invocations in requests
DATABASES["default"]["ATOMIC_REQUEST"] = True

# If the flag as been set, configure to use proxy
if _env("USE_CLOUD_SQL_AUTH_PROXY"):
    DATABASES["default"]["HOST"] = "127.0.0.1"
    DATABASES["default"]["PORT"] = 5432

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# APPLICATION DEFINITION

ROOT_URLCONF = "backend.urls"
INSTALLED_APPS = [
    "backend.contrib.tasks",
    "backend.contrib.l10n",
    "backend.core",
]
MIDDLEWARE = [
    "django_structlog.middlewares.RequestMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "backend.contrib.tasks.middleware.TaskEnvironmentMiddleware",
]


# INTERNATIONALIZATION

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

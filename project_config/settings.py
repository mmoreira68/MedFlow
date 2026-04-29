"""
Django settings for project_config
Pronto para deploy no Render: SQLite em disco + WhiteNoise.
"""

from pathlib import Path
import os


# =============================================================================
# Helpers
# =============================================================================

def env_bool(name: str, default: bool = False) -> bool:
    """Booleano de variável de ambiente."""
    v = os.environ.get(name)
    if v is None:
        return default
    return v.lower() in {"1", "true", "t", "yes", "y", "on"}


def env_csv(name: str, default: str = "") -> list[str]:
    """Lista separada por vírgulas a partir de env."""
    raw = os.environ.get(name, default)
    return [i.strip() for i in raw.split(",") if i.strip()]


# =============================================================================
# Paths
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# Execução / Segurança
# =============================================================================

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-key-do-not-use-in-production")
DEBUG = env_bool("DEBUG", True)

# Ex.: "seuapp.onrender.com,localhost,127.0.0.1"
ALLOWED_HOSTS = env_csv("ALLOWED_HOSTS", "*")

# Ex.: "https://seuapp.onrender.com,https://*.onrender.com"
CSRF_TRUSTED_ORIGINS = env_csv("CSRF_TRUSTED_ORIGINS", "")

# HTTPS por trás do proxy do Render (padrão seguro)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
_sp = os.environ.get("SECURE_PROXY_SSL_HEADER")
if _sp:
    parts = [p.strip() for p in _sp.split(",", 1)]
    if len(parts) == 2:
        SECURE_PROXY_SSL_HEADER = (parts[0], parts[1])

SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", not DEBUG)


# =============================================================================
# Apps
# =============================================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "medflow.apps.MedflowConfig",
]


# =============================================================================
# Middleware
# =============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise deve vir logo após SecurityMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =============================================================================
# URLs / WSGI
# =============================================================================

ROOT_URLCONF = "project_config.urls"
WSGI_APPLICATION = "project_config.wsgi.application"


# =============================================================================
# Templates
# =============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =============================================================================
# Banco de Dados
# - Defina SQLITE_PATH=/var/data/db.sqlite3 no Render (Disk).
# =============================================================================

SQLITE_PATH = os.environ.get("SQLITE_PATH", str(BASE_DIR / "db.sqlite3"))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": SQLITE_PATH,
    }
}


# =============================================================================
# Autenticação
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"


# =============================================================================
# i18n
# =============================================================================

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True


# =============================================================================
# Arquivos estáticos (WhiteNoise)
# =============================================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"      # destino do collectstatic
STATICFILES_DIRS = [BASE_DIR / "static"]    # se existir

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}


# =============================================================================
# Flags / Logging
# =============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
APPEND_SLASH = True

if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0")) or 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
    SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", True)

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "std": {"format": "[{asctime}] {levelname} {name}: {message}", "style": "{"}
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "std"}},
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
}

if DEBUG:
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = None

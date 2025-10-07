"""
Django settings for eismeaquiapp — Produção (PythonAnywhere)
MySQL interno + Gmail SMTP + pt-BR + static/media
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ───────────────── Segurança
SECRET_KEY = "d*31e^b948=qfjk-pw$uh(lh&4m)wes&r6gfkdnyb8ld+z^z%q"
DEBUG = False

ALLOWED_HOSTS = ["alexandremvdev.pythonanywhere.com"]
CSRF_TRUSTED_ORIGINS = ["https://alexandremvdev.pythonanywhere.com"]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# (Ative HSTS depois que tudo estiver estável em HTTPS)
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# ───────────────── Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Se você tiver apps próprias, adicione aqui. Ex.: "inscricoes",
    # "widget_tweaks", etc.
]

# ───────────────── Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "eismeaquiapp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # adicione pastas extra de templates se precisar
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

WSGI_APPLICATION = "eismeaquiapp.wsgi.application"

# ───────────────── Banco de dados — MySQL PythonAnywhere
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "alexandremvdev$default",
        "USER": "alexandremvdev",
        "PASSWORD": "Amv@1302",  # sua senha do MySQL no PA
        "HOST": "alexandremvdev.mysql.pythonanywhere-services.com",
        "PORT": "3306",
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        "CONN_MAX_AGE": 60,  # mantém conexões abertas (opcional)
    }
}

# ───────────────── Validação de senha
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ───────────────── i18n / timezone
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Araguaina"
USE_I18N = True
USE_TZ = True

# ───────────────── Static / Media
# No painel Web do PA mapeie:
#   /static/ -> /home/alexandremvdev/eismeaquiapp/static
#   /media/  -> /home/alexandremvdev/eismeaquiapp/media
STATIC_URL = "/static/"
STATIC_ROOT = "/home/alexandremvdev/eismeaquiapp/static"

MEDIA_URL = "/media/"
MEDIA_ROOT = "/home/alexandremvdev/eismeaquiapp/media"

# ───────────────── E-mail — Gmail SMTP (App Password sem espaços)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "alexandremv.dev@gmail.com"
EMAIL_HOST_PASSWORD = "jrnjnktsiaqbedko"  # App Password de 16 chars, sem espaços
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_TIMEOUT = 20

# ───────────────── Outras
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

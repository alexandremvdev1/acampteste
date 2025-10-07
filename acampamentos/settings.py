# acampamentos/settings.py — PRODUÇÃO PythonAnywhere (MySQL interno, Gmail SMTP)
from pathlib import Path
import os
from decimal import Decimal

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------------------
# Segurança / Produção
# ------------------------------------------------------------------------------
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']          # defina no PA (env var)
DEBUG = False

PA_USER = os.environ.get('PA_USER', 'SEU_USUARIO')    # defina no PA p/ facilitar
PA_DOMAIN = f"{PA_USER}.pythonanywhere.com"
SITE_DOMAIN = f"https://{PA_DOMAIN}"

ALLOWED_HOSTS = [PA_DOMAIN]
SITE_ID = 1

# Segurança web (ajuste se for usar domínio próprio também)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT   = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE    = True
CSRF_TRUSTED_ORIGINS  = [f"https://{PA_DOMAIN}"]

# (Opcional forte) HSTS em produção real com domínio definitivo:
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# ------------------------------------------------------------------------------
# Apps
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.sites',
    'widget_tweaks',

    'inscricoes',
]

# ------------------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'inscricoes.middleware.UserActivityLoggingMiddleware',
]

ROOT_URLCONF = 'acampamentos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # adicione pastas extras se tiver
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'acampamentos.wsgi.application'

# ------------------------------------------------------------------------------
# Banco de Dados — MySQL do PythonAnywhere
# (Confira os valores exatos na aba "Databases" do PA)
# ------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('PA_DB_NAME', f'{PA_USER}$default'),
        'USER': os.environ.get('PA_DB_USER', PA_USER),
        'PASSWORD': os.environ['PA_DB_PASSWORD'],  # defina no PA (env var)
        'HOST': os.environ.get('PA_DB_HOST', f'{PA_USER}.mysql.pythonanywhere-services.com'),
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ------------------------------------------------------------------------------
# Auth
# ------------------------------------------------------------------------------
AUTH_USER_MODEL = 'inscricoes.User'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------------------------------------------------------
# i18n / TZ
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Araguaina'
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# Static / Media (servidos pelo servidor de arquivos do PA)
# Mapeie no painel Web do PA:
#   /static/ -> /home/SEU_USUARIO/SEU_REPO/staticfiles
#   /media/  -> /home/SEU_USUARIO/SEU_REPO/media
# Rode: python manage.py collectstatic --noinput
# ------------------------------------------------------------------------------
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL   = '/media/'
MEDIA_ROOT  = BASE_DIR / 'media'

# ------------------------------------------------------------------------------
# E-mail — Gmail SMTP (recomendado: Conta com 2FA + App Password)
# ------------------------------------------------------------------------------
EMAIL_BACKEND        = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST           = 'smtp.gmail.com'
EMAIL_PORT           = 587
EMAIL_USE_TLS        = True
EMAIL_HOST_USER      = os.environ['EMAIL_HOST_USER']       # seu endereço Gmail
EMAIL_HOST_PASSWORD  = os.environ['EMAIL_HOST_PASSWORD']   # App Password (16 chars)
DEFAULT_FROM_EMAIL   = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Dicas:
# - Ative 2FA na conta Google e crie um "App Password" específico para SMTP.
# - NÃO use a senha normal da conta aqui.

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{asctime} | {levelname} | {name} | {message}", "style": "{"},
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "usuarios.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django":          {"handlers": ["file", "console"], "level": "INFO", "propagate": True},
        "django.security": {"handlers": ["file"], "level": "WARNING", "propagate": False},
    },
}

# ------------------------------------------------------------------------------
# Outras configs
# ------------------------------------------------------------------------------
FEE_DEFAULT_PERCENT = Decimal("5.0")

from pathlib import Path

# --------------------
# BASE DIR
# --------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------
# SEGURIDAD
# --------------------
SECRET_KEY = 'django-insecure-*wehmk--zmxbxnq3425b-1#)n(qi#(%5!jxw$c9i#&*d!q_2v4'

DEBUG = True

ALLOWED_HOSTS = []

# --------------------
# APLICACIONES INSTALADAS
# --------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # tu aplicación principal
]

# --------------------
# MIDDLEWARE (NECESARIO PARA /admin)
# --------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --------------------
# URLS y TEMPLATES
# --------------------
ROOT_URLCONF = 'agencia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # puedes usar [BASE_DIR / 'templates'] si usas una carpeta de plantillas global
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
AUTHENTICATION_BACKENDS = [
    'core.auth_backend.SQLServerAuthBackend',  # ajusta si tu app tiene otro nombre
    'django.contrib.auth.backends.ModelBackend',   # opcional, mantiene el backend por defecto
]


WSGI_APPLICATION = 'agencia.wsgi.application'

# --------------------
# BASE DE DATOS: SQL Server con autenticación de Windows
# --------------------
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'agencia_viajes',      # asegúrate que esta base ya existe en SQL Server
        'HOST': 'localhost\\SQLEXPRESS',    # o 'localhost\\SQLEXPRESS' si usas SQL Server Express
        'PORT': '',                    # deja vacío si es el puerto por defecto
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',  # o 'ODBC Driver 18 for SQL Server' si lo tienes
            'trusted_connection': 'yes',
        },
    }
}

# --------------------
# VALIDACIÓN DE CONTRASEÑAS
# --------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    
]

# --------------------
# INTERNACIONALIZACIÓN
# --------------------
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'

USE_I18N = True
USE_TZ = True

# --------------------
# ARCHIVOS ESTÁTICOS
# --------------------
STATIC_URL = 'static/'

# --------------------
# ID AUTOINCREMENTAL
# --------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

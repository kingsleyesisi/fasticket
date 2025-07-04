import os 
from pathlib import Path
from environ import Env
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env(str(BASE_DIR / '.env'))
# Initialize paystack secret key
PAYSTACK_SECRET_KEY = env('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = env('PAYSTACK_PUBLIC_KEY')


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-mx%5w1zkjb+_6(vm&fe*uqr%ohu^3(y$bch#a!$t_aq)hspkjc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')
# DEBUG = env('DEBUG')

# During production Trust Origin and Allowed Host should be set
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_authtoken',
    'rest_framework.authtoken',
    'corsheaders',

    'storages',

    # Local apps
    'Profile',
    'event_management',
    'payment',
    'ticket_management',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Ensure WhiteNoise is listed here

]

FRONTEND_URL = "http://localhost:3000"  # Change this to your frontend URL

ROOT_URLCONF = 'ticket.urls'

MAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')  # Use an App Password if using Gmail
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# NOTE this is not recommended for production just for debugging and testing during development
# CORS Settings
CORS_ALLOW_ALL = True

CORS_ALLOWED_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'HEAD',
    'OPTIONS',
]

# CORS_ALLOW_ALLOWED_METHODS = True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://fasticket.onrender.com',
    'http://localhost:8000',
    'https://fasticketss.vercel.app',
    'http://localhost:5173'
]
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ORIGIN_REGEX = r'^(https?:\/\/)?localhost(:[0-9]+)?$'

CORS_ALLOW_PUBLIC = True

CORS_ALLOW_PRIVATE = True

CORS_ALLOW_PROXY = True


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'ticket.wsgi.application'


# Database
# status = env('ENVIRONMENT', default='sqlite')
# if status == 'local':
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'db.sqlite3',
#         }
#     }
# elif status == 'production':
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql',
#             'NAME': env('POSTGRES_DATABASE'),
#             'USER': env('POSTGRES_USER'),
#             'PASSWORD': env('POSTGRES_PASSWORD'),
#             'HOST': env('POSTGRES_HOST', default='localhost'),  # Default to localhost if not set
#             'PORT': env('POSTGRES_PORT', default='5432'),  # Default PostgreSQL port
#         }
#     }
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': env('MYSQL_DATABASE'),
#         'USER': env('MYSQL_USER'),
#         'PASSWORD': env('MYSQL_PASSWORD'),
#         'HOST': env('MYSQL_HOST', default='localhost'),  # Default to localhost if not set
#         'PORT': env('MYSQL_PORT', default='3306'),  # Default MySQL port
#     }
# }



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Rest Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
        # 'rest_framework.permissions.IsAuthenticated',  # This Ensures that only authenticated users can access the API
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # This Ensures that only authenticated users can access the API
    ],
    'DEFAULT_THROTTLE_RATES': {
    'user': '10/min'  # Limit users to  requests per minute
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=6),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media Folder Settings
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'


DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000




CLOUDFLARE_R2_BUCKET = env('CLOUDFLARE_R2_BUCKET')
CLOUDFLARE_R2_ACCESS_KEY = env('CLOUDFLARE_R2_ACCESS_KEY')
CLOUDFLARE_R2_SECRET_KEY = env('CLOUDFLARE_R2_SECRET_KEY')
CLOUDFLARE_R2_BUCKET_ENDPOINT = env('CLOUDFLARE_R2_BUCKET_ENDPOINT')

CLOUDFLARE_R2_CONFIG_OPTIONS = {
    'bucket_name': CLOUDFLARE_R2_BUCKET,
    'access_key': CLOUDFLARE_R2_ACCESS_KEY,
    'secret_key': CLOUDFLARE_R2_SECRET_KEY,
    'endpoint_url': CLOUDFLARE_R2_BUCKET_ENDPOINT,
    'default_acl': 'public-read',
    'signature_version': 's3v4',
    'region_name': 'auto',
    'addressing_style': 'virtual',
}

STORAGES = {
    'default': {
        'BACKEND': 'helper.cloudflare.storages.MediaFileStorage',
        'OPTIONS': CLOUDFLARE_R2_CONFIG_OPTIONS,
    },
    'staticfiles': {
        'BACKEND': 'helper.cloudflare.storages.StaticFileStorage',
        'OPTIONS': CLOUDFLARE_R2_CONFIG_OPTIONS,
    },
}

import os 
from pathlib import Path
from environ import Env

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

    # Local apps
    'Profile',
    'Event_Manager',
    'payment',
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
]

ROOT_URLCONF = 'ticket.urls'




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
    'https://fasticket-react-w1x7.vercel.app',
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
        'DIRS': [],
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
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

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
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # This Ensures that only authenticated users can access the API
    ],
}

# Media Folder Settings
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
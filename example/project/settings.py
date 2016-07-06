# Django settings for example project.

import os

PROJECT_ROOT = os.path.normpath(
                 os.path.dirname(
                   os.path.realpath(__file__)))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

INSTALLED_APPS = (
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    #'debug_toolbar',
    'mptt',
    'yepes',
    'yepes.contrib.datamigrations',
    'yepes.contrib.registry',
    'yepes.contrib.sitemaps',
    'yepes.contrib.thumbnails',
    'marchena',
    'marchena.modules.authors',
    'marchena.modules.blogs',
    'marchena.modules.comments',
    'marchena.modules.links',
    'marchena.modules.posts',
)

# Cache settings.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Database settings.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'database.sqlite'),
    },
    #'default': {
        #'ENGINE':   'django.db.backends.postgresql_psycopg2',
        #'HOST':     'localhost',
        #'PORT':     '5432',
        #'NAME':     'marchena',
        #'USER':     'marchena',
        #'PASSWORD': 'marchena',
    #},
}

#Debug toolbar settings.
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    #'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    #'debug_toolbar.panels.profiling.ProfilingDebugPanel',
    #'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    #'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.cache.CacheDebugPanel',
    #'debug_toolbar.panels.signals.SignalDebugPanel',
    #'debug_toolbar.panels.logger.LoggingPanel',
)

# Grappelli settings.
GRAPPELLI_ADMIN_TITLE = u'Marchena'

# Internal IPs.
INTERNAL_IPS = (
    '127.0.0.1',
)

# Internationalization settings.
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Logging configuration.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Media settings.
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')
MEDIA_URL = '/media/'

# Middleware settings.
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# Security settings
ALLOWED_HOSTS = ['localhost']
ALLOWED_INCLUDE_ROOTS = [PROJECT_ROOT]
X_FRAME_OPTIONS = 'DENY'

# Sessions settings.
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Site settings.
SECRET_KEY = 'e0)ldd@7p%u%^+zc#_ib#s5f7an-qlv5e!9pkb=5ry^tq(yn@1'
SITE_ID = 1

# Static files settings.
STATIC_ROOT = ''
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

# Template settings.
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        os.path.join(PROJECT_ROOT, 'templates'),
    ],
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.request',
            'django.template.context_processors.static',
            'django.template.context_processors.tz',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
        'loaders': [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ],
    },
}]

# URL settings.
ROOT_URLCONF = 'project.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'project.wsgi.application'


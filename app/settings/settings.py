#  -------------------------------------------------------------------------
# | Settings in here will always be included (on any machine, dev or prod), |
# | and either settings_dev.py.py or settings_production.py will be included   |
# | (depending on whether the current host's network name is in the         |
# | HOSTS_PRODUCTION list in hosts.py                                       |
#  -------------------------------------------------------------------------

# First step: Import dev or prod specific settings
# ------------------------------------------------
import platform
import hosts
import datetime

# Grab the current machine's network name
host_local = platform.node()

# Import machine/environment specific settings
if host_local in hosts.HOSTS_PRODUCTION:
    print "Loading production settings"
    from settings_production import *
else:
    print "Loading dev settings"
    from settings_dev import *


# Helper for later (log files, etc)
NOW = datetime.datetime.now()
DATE_STR = NOW.strftime("%Y-%m-%d")

# Email setup
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = EMAIL_USER  # comes from settings_dev or _production
EMAIL_HOST_PASSWORD = EMAIL_PASS
EMAIL_USE_TLS = True

# Second step: Common settings
# ----------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'Europe/Vienna'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# Change in accordance with STATIC_ROOT to serve with outside webserver too
MEDIA_ROOT = '/opt/rpi-django/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/Users/chris/Projects/private/raspberrypi/projects/django/app/static/",
    "/opt/rpi-django/django/app/static/",
    )

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    )

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
    )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    )

if DEBUG:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

ROOT_URLCONF = 'app.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/Users/chris/Projects/private/raspberrypi/projects/django/app/templates",
    "/opt/rpi-django/django/app/templates",
    )

INSTALLED_APPS = (
    # Commonly required django internal apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Django admin interface
    'django.contrib.admin',

    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    # South is a tool to document and simplify database schema updates
    'south',

    # Redis status info for the admin interface
    #'redis_status',

    # Main app from the thermostat project
    'app.mainapp',
    'app.thermostat'
    )

if DEBUG:
    INSTALLED_APPS += ('debug_toolbar',)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default': {
            'format': '%(levelname)-8s %(asctime)s %(name)s \t%(message)s'
        },
        },

    # Handlers do something with log messages (eg. write to file, send email)
    'handlers': {
        # Handler for emailing admins on errors
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },

        # Handler for logging to a file
        'file':{
            'level':'INFO',
            'class':'logging.FileHandler',
            'formatter': 'default',
            'filename': "/opt/rpi-django/logs/django-%s.log" % DATE_STR,
            },

        # Handler for console output
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'default'
        },

        # Handler for /dev/null
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
            },
        },

    # What to log and where to
    'loggers': {
        # Mail admins on errors in request
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        },

    # This catches all python scripts logging messages
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
        }
}

# Step 3: Custom settings
# -----------------------
INTERNAL_IPS = ('127.0.0.1',)

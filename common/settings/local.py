from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default='^_xe!zh^)(7qi^qzzkl&m1ifhwtv==a2tvv5p=0z4*%!ta4(ux')

DEBUG = env.bool('DJANGO_DEBUG', default=True)
# set to false to prevent django-silk module from being loaded (it slows performance)
USE_SILK = env.bool('DJANGO_USE_SILK', default=False)

if USE_SILK and DEBUG:
    THIRD_PARTY_APPS += ('silk', )
    INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DJANGO_DB_DEFAULT_NAME'),
        'USER': env('DJANGO_DB_DEFAULT_USER'),
        'PASSWORD': env('DJANGO_DB_DEFAULT_PASSWORD'),
        'HOST': env('DJANGO_DB_HOST', default='localhost'),
        'PORT': env('DJANGO_DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': 'SET default_storage_engine=INNODB;',
            'sql_mode': 'STRICT_TRANS_TABLES',
        },
    },
    # 'legacy': {
        # 'ENGINE': 'django.db.backends.mysql',
        # 'NAME': env('DJANGO_DB_LEGACY_NAME'),
        # 'USER': env('DJANGO_DB_LEGACY_USER'),
        # 'PASSWORD': env('DJANGO_DB_LEGACY_PASSWORD'),
        # 'HOST': env('DJANGO_DB_HOST', default='localhost'),
        # 'PORT': '3306',
        # 'OPTIONS': {
            # 'sql_mode': 'STRICT_TRANS_TABLES',
            # 'init_command': 'SET '
                # 'storage_engine=INNODB,'
                # 'character_set_connection=utf8,'
                # 'collation_connection=utf8_bin'
        # },
    # },
}

DATABASE_ROUTERS = ['legacy.router.LegacyRouter']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if USE_SILK and DEBUG:
    MIDDLEWARE = ['silk.middleware.SilkyMiddleware',] + MIDDLEWARE

UCAMWEBAUTH_LOGIN_URL = 'https://demo.raven.cam.ac.uk/auth/authenticate.html'
UCAMWEBAUTH_LOGOUT_URL = 'https://demo.raven.cam.ac.uk/auth/logout.html'
UCAMWEBAUTH_CERTS = {901: """-----BEGIN CERTIFICATE-----
MIIDzTCCAzagAwIBAgIBADANBgkqhkiG9w0BAQQFADCBpjELMAkGA1UEBhMCR0Ix
EDAOBgNVBAgTB0VuZ2xhbmQxEjAQBgNVBAcTCUNhbWJyaWRnZTEgMB4GA1UEChMX
VW5pdmVyc2l0eSBvZiBDYW1icmlkZ2UxLTArBgNVBAsTJENvbXB1dGluZyBTZXJ2
aWNlIERFTU8gUmF2ZW4gU2VydmljZTEgMB4GA1UEAxMXUmF2ZW4gREVNTyBwdWJs
aWMga2V5IDEwHhcNMDUwNzI2MTMyMTIwWhcNMDUwODI1MTMyMTIwWjCBpjELMAkG
A1UEBhMCR0IxEDAOBgNVBAgTB0VuZ2xhbmQxEjAQBgNVBAcTCUNhbWJyaWRnZTEg
MB4GA1UEChMXVW5pdmVyc2l0eSBvZiBDYW1icmlkZ2UxLTArBgNVBAsTJENvbXB1
dGluZyBTZXJ2aWNlIERFTU8gUmF2ZW4gU2VydmljZTEgMB4GA1UEAxMXUmF2ZW4g
REVNTyBwdWJsaWMga2V5IDEwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBALhF
i9tIZvjYQQRfOzP3cy5ujR91ZntQnQehldByHlchHRmXwA1ot/e1WlHPgIjYkFRW
lSNcSDM5r7BkFu69zM66IHcF80NIopBp+3FYqi5uglEDlpzFrd+vYllzw7lBzUnp
CrwTxyO5JBaWnFMZrQkSdspXv89VQUO4V4QjXV7/AgMBAAGjggEHMIIBAzAdBgNV
HQ4EFgQUgjC6WtA4jFf54kxlidhFi8w+0HkwgdMGA1UdIwSByzCByIAUgjC6WtA4
jFf54kxlidhFi8w+0HmhgaykgakwgaYxCzAJBgNVBAYTAkdCMRAwDgYDVQQIEwdF
bmdsYW5kMRIwEAYDVQQHEwlDYW1icmlkZ2UxIDAeBgNVBAoTF1VuaXZlcnNpdHkg
b2YgQ2FtYnJpZGdlMS0wKwYDVQQLEyRDb21wdXRpbmcgU2VydmljZSBERU1PIFJh
dmVuIFNlcnZpY2UxIDAeBgNVBAMTF1JhdmVuIERFTU8gcHVibGljIGtleSAxggEA
MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEEBQADgYEAsdyB+9szctHHIHE+S2Kg
LSxbGuFG9yfPFIqaSntlYMxKKB5ba/tIAMzyAOHxdEM5hi1DXRsOok3ElWjOw9oN
6Psvk/hLUN+YfC1saaUs3oh+OTfD7I4gRTbXPgsd6JgJQ0TQtuGygJdaht9cRBHW
wOq24EIbX5LquL9w+uvnfXw=
-----END CERTIFICATE-----
"""}

if USE_AWS_S3:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_ACCESS_KEY_ID = env('DJANGO_AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('DJANGO_AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('DJANGO_AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = env('DJANGO_AWS_S3_ENDPOINT_URL')
    AWS_DEFAULT_ACL = env('DJANGO_AWS_DEFAULT_ACL', default='private')
    AWS_S3_REGION_NAME = env('DJANGO_AWS_S3_REGION_NAME', default='eu-west-2')

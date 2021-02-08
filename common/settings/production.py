from .base import *

SECRET_KEY = env('DJANGO_SECRET_KEY')

DEBUG = env.bool('DJANGO_DEBUG', default=False)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DJANGO_DB_DEFAULT_NAME'),
        'USER': env('DJANGO_DB_DEFAULT_USER'),
        'PASSWORD': env('DJANGO_DB_DEFAULT_PASSWORD'),
        'HOST': env('DJANGO_DB_HOST', default='localhost'),
        'PORT': '3306',
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

UCAMWEBAUTH_LOGIN_URL = 'https://raven.cam.ac.uk/auth/authenticate.html'
UCAMWEBAUTH_LOGOUT_URL = 'https://raven.cam.ac.uk/auth/logout.html'
UCAMWEBAUTH_CERTS = {2: """
-----BEGIN CERTIFICATE-----
MIIDrTCCAxagAwIBAgIBADANBgkqhkiG9w0BAQQFADCBnDELMAkGA1UEBhMCR0Ix
EDAOBgNVBAgTB0VuZ2xhbmQxEjAQBgNVBAcTCUNhbWJyaWRnZTEgMB4GA1UEChMX
VW5pdmVyc2l0eSBvZiBDYW1icmlkZ2UxKDAmBgNVBAsTH0NvbXB1dGluZyBTZXJ2
aWNlIFJhdmVuIFNlcnZpY2UxGzAZBgNVBAMTElJhdmVuIHB1YmxpYyBrZXkgMjAe
Fw0wNDA4MTAxMzM1MjNaFw0wNDA5MDkxMzM1MjNaMIGcMQswCQYDVQQGEwJHQjEQ
MA4GA1UECBMHRW5nbGFuZDESMBAGA1UEBxMJQ2FtYnJpZGdlMSAwHgYDVQQKExdV
bml2ZXJzaXR5IG9mIENhbWJyaWRnZTEoMCYGA1UECxMfQ29tcHV0aW5nIFNlcnZp
Y2UgUmF2ZW4gU2VydmljZTEbMBkGA1UEAxMSUmF2ZW4gcHVibGljIGtleSAyMIGf
MA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC/9qcAW1XCSk0RfAfiulvTouMZKD4j
m99rXtMIcO2bn+3ExQpObbwWugiO8DNEffS7bzSxZqGp7U6bPdi4xfX76wgWGQ6q
Wi55OXJV0oSiqrd3aOEspKmJKuupKXONo2efAt6JkdHVH0O6O8k5LVap6w4y1W/T
/ry4QH7khRxWtQIDAQABo4H8MIH5MB0GA1UdDgQWBBRfhSRqVtJoL0IfzrSh8dv/
CNl16TCByQYDVR0jBIHBMIG+gBRfhSRqVtJoL0IfzrSh8dv/CNl16aGBoqSBnzCB
nDELMAkGA1UEBhMCR0IxEDAOBgNVBAgTB0VuZ2xhbmQxEjAQBgNVBAcTCUNhbWJy
aWRnZTEgMB4GA1UEChMXVW5pdmVyc2l0eSBvZiBDYW1icmlkZ2UxKDAmBgNVBAsT
H0NvbXB1dGluZyBTZXJ2aWNlIFJhdmVuIFNlcnZpY2UxGzAZBgNVBAMTElJhdmVu
IHB1YmxpYyBrZXkgMoIBADAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBBAUAA4GB
AFciErbr6zl5i7ClrpXKA2O2lDzvHTFM8A3rumiOeauckbngNqIBiCRemYapZzGc
W7fgOEEsI4FoLOjQbJgIrgdYR2NIJh6pKKEf+9Ts2q/fuWv2xOLw7w29PIICeFIF
hAM+a6/30F5fdkWpE1smPyrfASyXRfWE4Ccn1RVgYX9u
-----END CERTIFICATE-----
"""}


if USE_AWS_S3:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = env('DJANGO_AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('DJANGO_AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('DJANGO_AWS_STORAGE_BUCKET_NAME')
    #AWS_S3_ENDPOINT_URL = env('DJANGO_AWS_S3_ENDPOINT_URL')
    AWS_DEFAULT_ACL = env('DJANGO_AWS_DEFAULT_ACL', default='private')
    AWS_S3_REGION_NAME = env('DJANGO_AWS_S3_REGION_NAME', default='eu-west-2')

STATIC_ROOT = str(WEBROOT_DIR('static'))
MEDIA_ROOT = str(WEBROOT_DIR('media'))

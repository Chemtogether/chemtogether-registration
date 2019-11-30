# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'change+this'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allowed hosts
ALLOWED_HOSTS = []

# Captcha keys, see https://www.google.com/recaptcha/, default ones are only allowed for localhost
RECAPTCHA_PUBLIC_KEY = '6Ldy8sQUAAAAAOCmFkVUxRytDcuhCzVsv5BuCjf5'
RECAPTCHA_PRIVATE_KEY = '6Ldy8sQUAAAAAAn7lpjcJfuitGe-Fv6OvqfLAQY4'


# Host for sending e-mail.
EMAIL_HOST = 'localhost'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Port for sending e-mail.
EMAIL_PORT = 25

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'Chemtogether Career Fair <info@chemtogether.ethz.ch>'


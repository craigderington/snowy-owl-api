import os

# secret key
SECRET_KEY = os.urandom(64)

# sql alchemy
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:deadbeef@localhost/lanternv2'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# mail
MAIL_SERVER = 'smtp.gmail.com'
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
MAIL_DEFAULT_SENDER = ''

# celery
CELERY_BROKER_URL = ''
CELERY_RESULT_BACKEND = ''
CELERY_ACCEPT_CONTENT = ''


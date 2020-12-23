import os

# secret key
SECRET_KEY = os.urandom(64)

# sql alchemy
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/beaconDB'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# mail
MAIL_SERVER = 'smtp.gmail.com'
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
MAIL_DEFAULT_SENDER = ''

# celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json'],


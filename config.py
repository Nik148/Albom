import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # JWT_SECRET_KEY = "super-secret"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=3600)
    FLASK_DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_EXTENSIONS = ('.jpg', '.png')
    UPLOAD_PATH = basedir + '/app/static/images/'
    POSTS_PER_PAGE = 3
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEBUG = os.environ.get('MAIL_DEBUG')
    ADMINS = ['Rogalik148@yandex.ru']
    LANGUAGES = ['en', 'ru']
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL') 
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
    DEBUG_TB_PROFILER_ENABLED = True
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL') or "redis://localhost:6379"
    CACHE_REDIS_HOST = os.environ.get('CACHE_REDIS_HOST') or 'localhost'
    CACHE_REDIS_PORT=6379
    CACHE_TYPE = 'RedisCache'
    CACHE_DEFAULT_TIMEOUT = 600

    # MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
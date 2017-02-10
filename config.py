import os
basedir = os.path.abspath(os.path.dirname(__file__))


Class Config(object):
      DEBUG = False
      TESTING = False
      PROPAGATE_EXCEPTIONS = True

      DATABASE_URI = os.environ.get('DATABASE_URI', 'postgresql://localhost/runner')
      SECRET_KEY = os.environ.get('SECRET_KEY', 'key')
      HOST_NAME = os.environ.get('APP_DNS', 'localhost')
      APP_NAME = os.environ.get('APP_NAME', 'runner')
      IP = os.environ.get('PYTHON_IP','127.0.0.1')
      PORT = int(os.environ.get('PYTHON_PORT', 8080))
      PG_DB_HOST = os.environ.get('POSTGRESQL_DB_HOST', 'localhost')
      PG_DB_PORT = int(os.environ.get('POSTGRESQL_DB_PORT', 5432))
      PG_DB_USERNAME = os.environ.get('POSTGRESQL_DB_USERNAME', 'saurav')
      PG_DB_PASSWORD = os.environ.get('POSTGRESQL_DB_PASSWORD', 'saurav ')

class ProductionConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

# web forms
# WTF_CSRF_ENABLED = True
# SECRET_KEY = 'saurav' 

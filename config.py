import os
#basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
      DEBUG = False
      TESTING = False
      PROPAGATE_EXCEPTIONS = True
      DATABASE_URI = 'postgresql://saurav:saurav@localhost/runner'

      # currently, not using these params
      SECRET_KEY = 'key'
      HOST_NAME = 'localhost'
      APP_NAME = 'runner1'
      PYTHON_IP = '127.0.0.1'
      PORT = int(8080)
      PG_DB_HOST = 'localhost'
      PG_DB_PORT = int(5432)
      PG_DB_USERNAME = 'saurav'
      PG_DB_PASSWORD = 'saurav '

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

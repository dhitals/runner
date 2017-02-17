from flask import Flask
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import Config

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

# if you want to restart the DB - set it somewhere else
recreate_if_exists = False

try:
    # connect to the default DB & check if APP_DB exists
    engine = create_engine('{0}://{1}:{2}@{3}/template1'.format('postgresql+psycopg2', 
                                                                Config.PG_DB_USERNAME,
                                                                Config.PG_DB_PASSWORD, 
                                                                Config.PG_DB_HOST,
                                                                'template1'))
    conn = engine.connect()

    existing_dbs = [ d[0] for d in \
                         conn.execute('SELECT datname from pg_database') ]

    # IFF both are true
    if Config.APP_NAME in existing_dbs and recreate_if_exists == True:
        conn.execute('COMMIT')
        conn.execute("""DROP DATABASE {}""".format(Config.APP_NAME))
            
    # IFF either is true
    if Config.APP_NAME not in existing_dbs or recreate_if_exists == True:
        conn.execute('COMMIT')
        conn.execute('CREATE DATABASE {}'.format(Config.APP_NAME))
        conn.execute('CREATE EXTENSION POSTGIS')
        
        print('Created new <{0}> DB'.format(Config.APP_NAME))

    conn.close()    
except:
    print('Could not connect to Postgres DB. Check your settings')
    raise

# now, go ahead and use the <RUNNER> DB
try:
    engine = create_engine('{0}://{1}:{2}@{3}/{4}'.format('postgresql+psycopg2',                                                                Config.PG_DB_USERNAME,
                                                          Config.PG_DB_PASSWORD, 
                                                          Config.PG_DB_HOST,
                                                          Config.APP_NAME))
    metadata = MetaData(bind=engine)
    Base = declarative_base(metadata=metadata) 
    Session = sessionmaker(bind=engine)

    # if the DB was newly created
    if Config.APP_NAME not in existing_dbs or recreate_if_exists == True:
        from app.models import User, Event, Run
        Base.metadata.create_all()
    
except:
    print('Could not find DB. Creating new <%s> DB.' %Config.APP_NAME)
    raise

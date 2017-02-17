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
    # print('Existing DBs: ', existing_dbs)
    
    # IFF both are true
    if Config.APP_NAME in existing_dbs and recreate_if_exists == True:
        conn.execute('COMMIT')
        conn.execute("""DROP DATABASE {}""".format(Config.APP_NAME))
            
    # IFF either is true
    if Config.APP_NAME not in existing_dbs or recreate_if_exists == True:
        conn.execute('COMMIT')
        conn.execute('CREATE DATABASE {}'.format(Config.APP_NAME))
        print('Created new DB <{}>'.format(Config.APP_NAME))

    # to enable spatial ref system
    # conn.execute('CREATE EXTENSION POSTGIS')
    # print('Enabled POSTGIS extension for <{}>'.format(Config.APP_NAME))
        
except:
    print('ERROR: Could not connect to Postgres DB. Check your settings\n')
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

    # if `users` table does not exist, assume no tables exist & create all
    if (conn.execute('select exists(select * from information_schema.tables where table_name=%s)', ('users',)).fetchone()[0]) is False:
        from app.models import User, Event, Run
        Base.metadata.create_all()
    
    conn.close()
except:
    print('Could not find DB. Creating new <%s> DB.' %Config.APP_NAME)
    raise

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData#, Table
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.automap import automap_base

#import psycopg2 as pg
from config import Config, DevelopmentConfig

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
from app import views


engine = create_engine('{0}://{1}:{2}@{3}/{4}'.format('postgresql+psycopg2',                                                                Config.PG_DB_USERNAME,
                                                      Config.PG_DB_PASSWORD, 
                                                      Config.PG_DB_HOST,
                                                      Config.APP_NAME))
metadata = MetaData(bind=engine)
Base = automap_base(metadata=metadata)
Base.prepare(engine, reflect=True)
metadata.reflect(engine)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
# Connection = engine.connect()


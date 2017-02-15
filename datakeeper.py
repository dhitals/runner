import numpy as np
import pandas as pd
import psycopg2 as pg
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import table, column, select, update, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base

from app import app
from config import Config


class datakeeper():
    
    def __init__(self, recreate_if_exists=False, verbose=True):

        engine_params = ['postgresql+psycopg2', Config.PG_DB_USERNAME,
                         Config.PG_DB_PASSWORD, Config.PG_DB_HOST, Config.APP_NAME]
        try:
            # connect to the default DB & check if APP_DB exists
            engine = create_engine('{0}://{1}:{2}@{3}/template1'.format('postgresql+psycopg2', 
                                                                        Config.PG_DB_USERNAME,
                                                                        Config.PG_DB_PASSWORD, 
                                                                        Config.PG_DB_HOST,
                                                                        'template1'))
        except:
            print('Error connecting to Postgres DB.\n')
            raise
            
        conn = engine.connect()
        
        existing_dbs = [ d[0] for d in \
                         conn.execute("SELECT datname from pg_database") ]

        # IFF both are true
        if Config.APP_NAME in existing_dbs and recreate_if_exists == True:
            conn.execute("commit")
            conn.execute("""DROP DATABASE {}""".format(Config.APP_NAME))
            
        # IFF either is true
        if Config.APP_NAME not in existing_dbs or recreate_if_exists == True:
            conn.execute("commit")
            conn.execute("CREATE DATABASE {}".format(Config.APP_NAME))
            
            print("Created new <{0}> DB".format(Config.APP_NAME))

        conn.close()
                        
        # go ahead, connect to the APP DB
        self.engine = create_engine('{0}://{1}:{2}@{3}/{4}'.format('postgresql+psycopg2', 
                                                                   Config.PG_DB_USERNAME,
                                                                   Config.PG_DB_PASSWORD, 
                                                                   Config.PG_DB_HOST,
                                                                   Config.APP_NAME))
        self.connection = engine.connect()
        self.metadata = MetaData(bind=self.engine)
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = automap_base(metadata=self.metadata)
        self.Base.prepare(self.engine, reflect=True)
        
        self.metadata.reflect(self.engine) #, schema=self.dbName)
        
        # create the tables
        from models import User, Event, Run
        self.Base.metadata.create_all()
        
        return
    

    def add_user(self, username, email, password=None, fname=None, lname=None):
        s = self.Session()
        try:
            ins = self.Base.classes.User(username=username, email=email, password=password,
                                         fname=fname, lname=lname)
            q = s.add(ins)
            s.commit()
            s.close()
            return int(ins.id)
        except:
            s.rollback()
            s.close()
            raise
        
            

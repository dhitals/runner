import numpy as np
import pandas as pd
import psycopg2 as pg
from sqlalchemy import create_engine, MetaData, Table

from models import User
from config import Config

class data_keeper():
    
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

        if Config.APP_NAME not in existing_dbs:
            print("No existing DB. Created <{0}>".format(Config.APP_NAME))
            conn.execute("CREATE DATABASE {}".format(Config.APP_NAME))
            
        # go ahead, connect to the APP DB    
        self.engine = create_engine('{0}://{1}:{2}@{3}/{4}'.format('postgresql+psycopg2', 
                                                                   Config.PG_DB_USERNAME,
                                                                   Config.PG_DB_PASSWORD, 
                                                                   Config.PG_DB_HOST,
                                                                   Config.APP_NAME))
        self.connection = engine.connect()
        self.metadata = MetaData(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.Base = automap_base(metadata=self.metadata)
        self.Base.prepare(self.engine, reflect=True)
        self.metadata.reflect(self.engine) #, schema=self.dbName)
        
        # Init db if necessary (i.e. no tables exist). 
        self.init_db(recreate_if_exists=recreate_if_exists, verbose=verbose)
        
        conn.close()

        return
    
        def init_db(self, recreate_if_exists=False, verbose=True):
            """ Create tables if they don't exist. 
            if 'recreate_if_exists' is set to True then drop existing & recreate """
            
            if recreate_if_exists == True:
                conn.set_isolation_level(0)
                cur.execute("""DROP DATABASE {}""".format(self.dbName))


        def add_user(self, username, password, fname=None, lname=None):
            s = self.Session()
            try:
                ins = self.Base.classes.User(username=username, password=password,
                                             fname=fname, lname=lname)
                q = s.add(ins)
                s.commit()
                return int(ins.id)
            except:
                s.rollback()
                raise
            s.close()

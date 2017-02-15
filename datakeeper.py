import os, sys, glob
import numpy as np
import pandas as pd
#import psycopg2 as pg

#from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import table, column, select, update, insert
#from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError, OperationalError, SQLAlchemyError

import gpxpy
import geopandas as gpd
from shapely.geometry import Point

from app import app, engine, Base, Session
from app.models import User, Event, Run
#from config import Config


class datakeeper():

    def __init__(self):
        pass

    def add_user(self, username, email, fname=None, lname=None, password=None):

        s = Session()
        try:
            u = User(username=username, email=email,
                     fname=fname, lname=lname, password=password)
            s.add(u)
            s.commit()

            print(u.id)

            return int(u.id)
        except SQLAlchemyError as err:
            s.rollback()
            raise
        
        s.close()
    
    def add_events(self, user_id, path=None):

        if path is None:
            path = '/Users/saurav/projects/runner/data/'

        events, runs = [], []

        files = glob.glob(path+'*Run*.gpx')

        for file in files[0:3]:
            gpx_file = open(file, 'r')
            gpx = gpxpy.parse(gpx_file)

            for t in gpx.tracks:
                for j, s in enumerate(t.segments):
                    events.append([t.name, t.get_time_bounds().start_time, t.length_3d(), 
                                   t.get_duration(), t.get_moving_data().max_speed, 
                                   os.path.basename(file)])
                    for i, p in enumerate(s.points):
                        runs.append([t.get_time_bounds().start_time,
                                     p.time, p.latitude, p.longitude, p.elevation, s.get_speed(i)])

        events = pd.DataFrame(events,
                              columns=['name', 'start_time', 'distance',
                                       'duration', 'max_speed', 'filename'])

        events.distance = events.distance / 1.6e3 # meters --> miles
        # events.duration = pd.to_timedelta(events.duration, unit='s')
        events.max_speed = events.max_speed * (3600./1.6e3) # m/s --> mph
        events['year']  = events.start_time.apply(lambda x: x.year)
        events['month'] = events.start_time.apply(lambda x: x.month)
        events['week']  = events.start_time.apply(lambda x: x.week)

        events['run_type'] = ' '
        events['avg_speed'] = 0.
        events['avg_pace'] = 0.
        events['avg_heartrate'] = 0.
        events['avg_cadence'] = 0.
        events['source'] = ''
        events['shoes'] = ''
        events['user_id'] = user_id

        print(events.shape)
        
        try:
            s = Session()
            events.to_sql('events', engine, if_exists='append', index=False)
            s.commit()
            s.close()
        except SQLAlchemyError as err:
            raise

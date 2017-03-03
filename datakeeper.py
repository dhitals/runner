import os, sys, glob
import numpy as np
import pandas as pd

from flask import abort, request
from sqlalchemy.sql import table, column, select, update, insert
from sqlalchemy.exc import InvalidRequestError, OperationalError, SQLAlchemyError, ProgrammingError

import gpxpy
import geopandas as gpd
#from shapely.geometry import Point
#import shapely.wkb
import units

from app import app, Base, engine, Session
from app.models import User, Event, Run

from stravalib.client import Client
from app.apikey import CLIENT_ID, CLIENT_SECRET

import matplotlib.pyplot as plt

""" 
SQLAlchemy and psycopg2 do not understand geometry. So when reading / writing 
to POSTGIS, one needs to convert to  binary or hex, generally using shapely.wkb.

For writing, I am currently writing lon/lat to DB and then adding a geometric 
column using raw SQL. So the `app.model.runs` table looks different from RUNS table.
When appending data, this will necessitate first writing to a temporary table.

"""
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
            return int(u.id)
        except SQLAlchemyError as err:
            s.rollback()
            print('Error: \n', err)
            raise
        
        s.close()

    def get_pace(self, speed):
        " convert from spped (m/s) to pace (miles/min) """
        pace = 60. / speed


    
    def add_event(self, user_id, path=None):

        if path is None: # IFF starting from scratch
            path = '/Users/saurav/projects/runner/data/*Run*.gpx'
        # get the list of files to import
        files = glob.glob(path)

        events, runs = [], []
        # process and import each file one at a time
        for file in files:
            gpx_file = open(file, 'r')
            gpx = gpxpy.parse(gpx_file)

            for t in gpx.tracks:
                for j, s in enumerate(t.segments):
                    for i, p in enumerate(s.points):
                        runs.append([p.time, p.latitude, p.longitude, p.elevation, s.get_speed(i)])

            s = Session()
            try:
                # prep the event data
                event = Event(name=t.name,
                              datetime=t.get_time_bounds().start_time,
                              run_type='',
                              distance=t.length_3d() / 1.6e3, # meters --> miles
                              duration=t.get_duration(),
                              max_speed=t.get_moving_data().max_speed * (3600./1.6e3), # m/s --> mph
                              avg_speed=0,
                              avg_pace=0,
                              avg_heartrate=0,
                              avg_cadence=0,
                              source='',
                              shoes='',
                              filename=os.path.basename(file),
                              user_id=user_id)                            
                s.add(event)
                s.commit()
                event_id = int(event.id)
            except SQLAlchemyError as err:
                s.rollback()
                print('Error: Cannot write event to DB. \n', err)
                raise

            # prep the run data -- use pands for this
            runs = pd.DataFrame(runs,
                                columns=['time', 'latitude', 'longitude', 'altitude', 'speed'])
            #runs['point'] = [ Point(xy) for xy in zip(runs.longitude, runs.latitude) ]

            runs = pd.DataFrame(runs)#, crs=None, geometry=pt)
            runs['heartrate'] = 0.
            runs['cadence'] = 0.
            runs['user_id'] = user_id
            runs['event_id'] = event_id

        try:
            # write df to sql
            runs.to_sql('runs', engine, if_exists='append', index=False)
            # add a column `coords` to the table
            s.execute("SELECT AddGeometryColumn('runs', 'coords', 4326, 'POINT', 2);")
            s.commit()
            # now, convert lon/lat to coords
            s.execute("UPDATE runs SET coords=ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);")                        

            s.commit()
            s.close()
        except SQLAlchemyError as err:
            raise

        


    
class summary():

    def __init__(self):
        pass
    
    def summarize(self, df, groupby=None):
    
        df = df.copy()
        cols_to_drop = [ col for col in df.columns if 'id' in col or 'name' in col ]
        df.drop(cols_to_drop, axis=1, inplace=True)
        
        if groupby == 'year':
            groupby = df.index.year
        elif groupby == 'month':
            groupby = [df.index.year, df.index.month]
        elif groupby == 'week':
            groupby = [df.index.year, df.index.week]
    
        try:
            g = df.groupby(groupby).mean()
            g_sum  = df.groupby(groupby).sum()
            g_max  = df.groupby(groupby).max()
        except:
            print('Error: Your `groupby` variable is not valid.')
            
        g.rename(columns={'distance': 'avg_distance', 
                          'duration': 'avg_duration'}, inplace=True)
        g['n_activities'] = df.groupby(groupby)['distance'].count()
        g['total_distance'] = g_sum['distance']
        g['total_duration'] = g_sum['duration']
        g['max_distance'] = g_max['distance']
        g['max_duration'] = g_max['duration']
            
        return g

    def plot(self, df):
        fig, ax = plt.subplots(3,3, figsize=(16,10))
        
        df.plot(y='total_distance', kind='bar', ax=ax[0,0])
        df.plot(y='avg_distance', kind='bar', ax=ax[0,1])
        df.plot(y='max_distance', kind='bar', ax=ax[0,2])
        
        df.plot(y='total_duration', kind='bar', ax=ax[1,0])
        df.plot(y='avg_duration', kind='bar', ax=ax[1,1])
        df.plot(y='max_duration', kind='bar', ax=ax[1,2])
        
        return

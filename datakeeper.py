import os, sys, glob
import numpy as np
import pandas as pd

from sqlalchemy.sql import table, column, select, update, insert
from sqlalchemy.exc import InvalidRequestError, OperationalError, SQLAlchemyError, ProgrammingError

import gpxpy
import geopandas as gpd
from shapely.geometry import Point
#import shapely.wkb

from app import app, Base, Session
from app.models import User, Event, Run

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
    
    def add_event(self, user_id, path=None):

        if path is None: # IFF starting from scratch
            path = '/Users/saurav/projects/runner/data/*Run*.gpx'
        # get the list of files to import
        files = glob.glob(path)

        events, runs = [], []
        # process and import each file one at a time
        for file in files[0:1]:
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
                                columns=['time', 'latitude', 'longitude', 'elevation', 'speed'])
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

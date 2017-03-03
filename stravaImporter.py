import numpy as np
import pandas as pd

from flask import abort, request
from sqlalchemy.sql import table, column, select, update, insert
from sqlalchemy.exc import InvalidRequestError, OperationalError, SQLAlchemyError, ProgrammingError

import gpxpy
import geopandas as gpd
#from shapely.geometry import Point
#import shapely.wkb

from app import app, Base, engine, Session
from app.models import Activity, User

from stravalib.client import Client
from app.apikey import CLIENT_ID, CLIENT_SECRET

""" Util to import Strava data and store it in PostGres DB.

    Ignoring GIS support for now. Look at the GPX import for GIS-enabling.

"""

class stravaImporter(object):
    
    def __init__(self):
        self.client = Client()
        self.API_CALL_PAUSE_SECONDS = 1.5  # 40 requests per minute
        
        url = self.client.authorization_url(client_id=CLIENT_ID, 
                               redirect_uri='http://localhost:5000/authorization')

        url = 'http://www.strava.com/oauth/authorize?client_id=16424&response_type=code&redirect_uri=http://localhost/5001&approval_prompt=force&scope=write'
        print(url)

        #code = request.args.get('code') # or whatever your framework does
        code = 'ccb3d9e9f3e1114eb0d4b59b086f44268c3cfd96'
        access_token = self.client.exchange_code_for_token(client_id=CLIENT_ID, 
                                                           client_secret=CLIENT_SECRET,
                                                           code=code)        
        # Now store that access token somewhere (a database?)
        self.client.access_token = access_token
        
        # retrieve the athlete
        self.athlete = self.client.get_athlete()
        print("For {}, I now have an access token".format(self.athlete.id))

        self.streams = ['time', 'latlng', 'distance', 'altitude', 'velocity_smooth',
                        'heartrate', 'cadence', 'temp', 'moving', 'grade_smooth' ]
        
    def get_activities(self, before=None, after=None, limit=None):
        return list(self.client.get_activities(before=before, after=after, limit=limit))
    
    def get_streams(self, activity_id):
        # download the entire stream: `resolution` = `all` (default)
        # download all stream_types except `power`
        return self.client.get_activity_streams(activity_id, types=self.streams)
    
    def get_DF(self, s):
        """ Convert a Strava Stream to a pandas DF """
        return pd.DataFrame.from_dict({ k: s[k].data for k in s.keys() })

    def add_user(self, username, email=None, fname=None, lname=None, password=None):
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

    def add_activity(self, user_id, before=None, after=None, limit=None):
        """ Get & add a list of activities from strava """
        
        # get the list of activities from strava
        activities = self.get_activities(before=before, after=after, limit=limit)
        # transform activities to a DF ready for Postgres
        df = self.munge_activity(activities)
        df['user_id'] = user_id
        
        s = Session()
        try:
            df.to_sql('runs', engine, if_exists='append', index=False)
            s.commit()
        except:
            s.rollback()
            print('Error: Cannot write event to DB. \n')
            raise            


    def strip_units(self, df, cols):
        """ strip units from columns -- changes dtype from `object` to `float`"""

        d = {'average_speed': ' m / s',
             'max_speed': ' m / s',
             'distance': ' m',
             'total_elevation_gain': ' m'}      
        
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype('str').str.strip(d[col]), errors='coerce')

        return df

    def munge_activity(self, activities):
        """ Get `activities` ready for Postgres DB """

        # `stravalib`.`activity` attributes to import
        fields =  ['athlete_count', 'average_cadence', 'average_heartrate',
                   'average_speed', 'distance', 'elapsed_time',
                   'elev_high', 'elev_low', 'end_latlng', 'external_id',
                   'gear_id', 'has_heartrate', 'id',
                   'location_city', 'location_country', 'location_state',
                   'manual', 'max_heartrate', 'max_speed', 'moving_time',
                   'name', 'pr_count', 'start_date', 'start_date_local',
                   'start_latitude', 'start_latlng', 'start_longitude',
                   'suffer_score', 'timezone', 'total_elevation_gain',
                   'type', 'upload_id', 'workout_type']
        
        # convert `activities` into a df with `fields` as columns
        df = pd.DataFrame([[getattr(i,j) for j in fields] for i in activities], columns=fields)
        
        # rename since `id` will be an internal DB `id`
        df.rename(columns={'id': 'strava_id'}, inplace=True)

        # pandas or SQL does not support units, so strip the units from the fields
        # could be worth adding units when the tables are imported
        # I want GIS support, so can't really move to JSONB or BSON
        cols_to_strip = ('average_speed', 'max_speed', 'distance', 'total_elevation_gain')
        df = self.strip_units(df, cols_to_strip)

        return df

import numpy as np
import pandas as pd
import time

from flask import abort, request
from sqlalchemy.sql import table, column, select, update, insert
from sqlalchemy.exc import InvalidRequestError, OperationalError, SQLAlchemyError, ProgrammingError

import gpxpy
import geopandas as gpd
#from shapely.geometry import Point
#import shapely.wkb

from app import app, Base, engine, Session
from app.models import Activity, User, Streams, User

from stravalib.client import Client
from app.apikey import CLIENT_ID, CLIENT_SECRET, ACCESS_CODE

""" Util to import Strava data and store it in PostGres DB.

    Ignoring GIS support for now. Look at the GPX import for GIS-enabling.
"""

class stravaImporter(object):
    
    def __init__(self):
        self.client = Client()
        self.API_CALL_PAUSE_SECONDS = 1.5  # 40 requests per minute
        
        # this is NOT working right now -- FIX -- using hard-coded URL / ACCESS_CODE right now
        #url = self.client.authorization_url(client_id=CLIENT_ID, 
        #                       redirect_uri='http://localhost:5000/authorization')
        #code = request.args.get('code') # or whatever flask does

        url = 'http://www.strava.com/oauth/authorize?client_id=16424&response_type=code&redirect_uri=http://localhost/5001&approval_prompt=force&scope=write'
        print(url)
        
        access_token = self.client.exchange_code_for_token(client_id=CLIENT_ID, 
                                                           client_secret=CLIENT_SECRET,
                                                           code=ACCESS_CODE)        
        # Now store that access token somewhere (a database?)
        self.client.access_token = access_token
        
        # retrieve the athlete
        self.athlete = self.client.get_athlete()
        print("For {}, I now have an access token".format(self.athlete.id))

        # name of tables in model
        self.user_TBL = 'users'
        self.activity_TBL = 'activities'
        self.streams_TBL = 'streams'
        self.gear_TBL = 'gear'

        # streams to extract from strava
        self.streams = ['time', 'latlng', 'distance', 'altitude', 'velocity_smooth',
                        'heartrate', 'cadence', 'temp', 'moving', 'grade_smooth' ]
        
    def get_activities(self, before=None, after=None, limit=None):
        """ Get activities and the related metadata from strava """
        return list(self.client.get_activities(before=before, after=after, limit=limit))
    
    def get_streams(self, activity_id):
        # download the entire stream: `resolution` = `all` (default)
        # download all stream_types except `power`
        try:
            s = self.client.get_activity_streams(activity_id, types=self.streams)
            return 
        except:
            print('Could not get streams for activity {0}. Manual upload?'.format(activity_id))
            return

    def stream_to_DF(self, s):
        """ Convert a Strava Stream to a pandas DF """
        return pd.DataFrame.from_dict({ k: s[k].data for k in s.keys() })

    def add_user(self, username, email=None, fname=None, lname=None, password=None):
        s = Session()
        try:
            u = User(username=username, email=email,
                     fname=fname, lname=lname, password=password,
                     strava_id=self.athlete.id)
            s.add(u)
            s.commit()
            return int(u.id)
        except SQLAlchemyError as err:
            s.rollback()
            print('Error: \n', err)
            raise

        s.close()
        return

    def add_activity(self, user_id, before=None, after=None, limit=None, add_streams=True):
        """ Get & add a list of activities from strava """
        
        # get the list of activities from strava
        activities = self.get_activities(before=before, after=after, limit=limit)
        # transform activities to a DF ready for Postgres
        df = self.munge_activity(activities)
        df['user_id'] = user_id
        
        s = Session()
        try:
            df.to_sql(self.activity_TBL, engine, if_exists='append', index=False)
            s.commit()            
            print('Added {0} activities from Strava.\n'.format(len(df.strava_id)))
        except:
            s.rollback()
            print('Error: `add_activity` cannot write event to DB. \n')
            raise
        s.close()

        # if needed, add the streams as well
        if add_streams is True:
            size = len(df.strava_id)
            for (i, strava_id) in enumerate(df.strava_id):
                print('Fetching data streams for {0}: {1} of {2}'.format(strava_id, i, size), end='\r')
                time.sleep(self.API_CALL_PAUSE_SECONDS) # limit API call to 40 / min

                self.add_streams(user_id, strava_id)
            print('Added `Streams` for {0} activities from Strava.'.format(len(df.strava_id)))

        return

    def add_streams(self, user_id, s_id):
        """ Add Strava data streams for a given user_id and activity_id """                

        # get the strava streams for that activity
        stream = self.get_streams(s_id)
        # convert the streams to a DF
        if stream is not None:
            s = Session()

            df = self.stream_to_DF(stream)

            # add activity_id to the DF
            df['activity_id'] = s.query(Activity.id).filter_by(strava_id=s_id.astype(str)).one()[0]
        
            try:
                df.to_sql(self.streams_TBL, engine, if_exists='append', index=False)
                s.commit()
            except:
                s.rollback()
                print('Error: `add_streams` cannot write event to DB. \n')
                raise

            s.close() 
        return

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

        # pd.to_sql does not yet support TZ, so strip it. for now.
        # also does not suport timedelta ... maybe I have to ditch `pd.to_sql`
        # https://github.com/pandas-dev/pandas/issues/9086
        df.start_date = pd.DatetimeIndex(df.start_date).tz_convert(None)
        df.timezone = df.timezone.astype(str)
        return df

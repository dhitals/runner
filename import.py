from stravalib.client import Client
from flask import abort, request

from app.apikey import CLIENT_ID, CLIENT_SECRET

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

        self.types = ['time', 'latlng', 'altitude', 'heartrate', 'temp' ]
        
    def get_activities(self, before=None, after=None, limit=None):
        return list(self.client.get_activities(before=before, after=after, limit=limit))
    
    def get_streams(self, activity_id):
        streams = self.client.get_activity_streams(activity_id, 
                                                   types=self.types, 
                                                   series_type='time')
    
        return streams    

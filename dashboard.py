"""
   Dashboard used to run the runner app -- will be replaced by a GUI interface
"""
from app import app, Session
from stravaImporter import stravaImporter

## import data from Strava API

# instantiate the strava object
strava = stravaImporter()

try:
    s = Session()
	# get user_id    
	user_id = s.query(User.id).filter_by(username='saurav').one()[0]
    s.close()
except:
    print('User does not exist in system. Creating a new one...')
    try:
	    user_id = strava.add_user('saurav', 
    	                          email='saurav@email.com', 
        	                      fname='saurav', 
            	                  lname='dhital')
	except:
    	print("Error: Cannot create new user.\n")
    	raise    

# get & store the list of ALL activities from strava
activities = strava.add_activity(user_id)

# update (sync) activities using the last activity date
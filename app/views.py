import glob
import numpy as np
import pandas as pd
import stravalib
from flask import jsonify, redirect, render_template, request, send_file, url_for

import matplotlib.pyplot as plt
from io import BytesIO
import base64

from app import app, engine, Session
from app.apikey import CLIENT_ID, CLIENT_SECRET
from app.models import User, Activity, Streams
from app.maps import get_map
from app.utils import summarize

#from stravaImporter import stravaImporter
#dk = stravaImporter()

username, user_id = 'saurav', 1

@app.route('/')
def index():
    return render_template('index.html', username=username)

@app.route('/activities')
@app.route('/activities?sort=<var>')
def view_activities(user_id=1):
    """ View a list of all activities """
    s = Session()

    try: var
    except NameError: var = None

    try:
        # define sort_order -- passed in <var> is primary
        so = ['user_id', 'id', 'start_date', 'distance', 'moving_time']
        if var:
            so.insert(0, var) 

        r = s.query(Activity)\
             .filter(Activity.user_id == user_id)\
                             .order_by(so[0], so[1], so[2], so[3], so[4]).all()
        
        return(render_template('activities.html', username='saurav', activities=r))
    except:
        s.rollback()
        s.close()
        raise       

@app.route('/maps/<int:id>.html')
def show_map(id):
    """ GIven an activity ID, get and show the map """
    return send_file('./static/maps/{0}.html'.format(id))

#@app.route('/activity', methods=['GET', 'POST'])
@app.route('/activity/<int:id>', methods=['GET', 'POST'])
""" View an activity """
def view_activity(id):
    try:
        q = "SELECT * FROM {0} WHERE activity_id={1}".format('streams', id)
        df = pd.read_sql_query(q, engine)        
    except: 
        print('Check DB connection: I cannot retrieve activity.')   

    # get run coordinates as a list of tuple of (lat, lon)
    coords = [ (float(x[1:-2].split(',')[0]), 
                float(x[1:-2].split(',')[1])) for x in df.latlng ]

    # get a folium map for the coords
    get_map(id, coords, z=df.velocity_smooth)

    return render_template('activity.html', id=id)

@app.route('/summary')
@app.route('/summary_plot')
def summary_plot():
    """ View the Summary Plot of your activities by date range and summarizing frequency """

    summ = summarize('saurav')    
    plot_url = summ.plot(return_b64=True)

    return render_template('summary_plot.html', plot_url=plot_url)

@app.route('/summary_table')
def summary_table():
       """ View the Summary Table of your activities by date range and summarizing frequency """
 
    summ = summarize(username)
    df = summ.pprint()
    
    return render_template("summary_table.html", data=df.to_html(classes='longtable'))

@app.route('/add', methods=['GET', 'POST'])
def add_user():
    """ Add a user from the GUI interface"""
    s = Session()
    try:
        u = User(username='saud', email='email22@gmail.com', 
                 fname='me', lname='me', password='me')
        s.add(u)
        s.commit()
        s.close()
        
        flash ("User %s added" %u.username)
        return int(u.id)
    except:
        s.rollback()
        s.close()
        raise

### --------------------------------
### Templates for Jinja conversions.
### --------------------------------

@app.template_filter('ns_to_hms')
def ns_to_hms(x):
    """ Convert time units: nanosecond to hour """
    hh = x * 1e-9 * 0.000277778 # ns --> s --> hr
    
    hms = [str(int(hh)), 
           str(int(hh * 60) % 60).zfill(2),
           str(int(hh * 2660) % 60).zfill(2)]
    
    hms = ':'.join(hms) if hh >= 1 else ':'.join(hms[1:])
    
    return hms

@app.template_filter('m_to_mile')
def m_to_mile(x):
    """ convert distance from meter to miles """
    return (x * 0.000621371) # meter --> mile

@app.template_filter('speed_to_pace')
def speed_to_pace(x):
    """ convert speed in m/s to pace in min/mile """
    if x == 0:
        return 0
    else:
        p = 26.8224 / x # 1 m/s --> min/mile

        return ':'.join([str(int(p)),                 
                         str(int((p * 60) % 60)).zfill(2)])

@app.template_filter('calc_speed')
def calc_speed_filter(t):
    return pd.to_timedelta(t, unit='s')

@app.template_filter('get_date')
def get_date_filter(dt):
    return dt.date()

@app.template_filter('get_time')
def get_time_filter(dt):
    return dt.time()

@app.route("/auth")
def auth_callback():
    API_CLIENT = stravalib.Client()
    code = request.args.get('code')
    access_token = API_CLIENT.exchange_code_for_token(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        code=code
        )
    return access_token

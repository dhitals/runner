import glob
import numpy as np
import pandas as pd
from flask import render_template, jsonify, request, flash, redirect, url_for
import pint

from app import app, Session
from app.models import User, Event, Run


@app.route('/')
def index():
    return render_template('index.html', username='saurav')

@app.route('/activities')
@app.route('/activities?sort=<var>')
def view_activities(user_id=1):
    s = Session()

    try: var
    except NameError: var = None

    try:
        # define sort_order -- passed in <var> is primary
        so = ['duration', 'start_time', 'user_id', 'distance']
        if var is not None: so = so.insert(0, var)

        print(so[0])
        
        events = s.query(Event).filter(Event.user_id == user_id).all()#order_by(so[0], so[1], so[2]).all()

        return(render_template('activities.html', username='saurav', events=events))
    except:
        s.rollback()
        s.close()
        raise       

@app.route('/add', methods=['GET', 'POST'])
def add_user():

    s = Session()
    try:
        u = User(username='me22', email='email22@gmail.com', 
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
    
@app.template_filter('convert_to_sexagesimal')
def convert_to_sexagesimal_filter(t):
    return pd.to_timedelta(t, unit='s')

@app.template_filter('calc_speed')
def calc_speed_filter(t):
    return pd.to_timedelta(t, unit='s')

@app.template_filter('get_date')
def get_date_filter(dt):
    return dt.date()

@app.template_filter('get_time')
def get_time_filter(dt):
    return dt.time()

@app.template_filter('convert_mph')
def convert_mph_filter(speed):
    ureg = pint.UnitRegistry()
    
    d, t = 1 * ureg.meter, 1 * ureg.second
    speed *= d/t

    return speed.to(ureg.miles / ureg.hour).magnitude

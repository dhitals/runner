import glob
from flask import render_template, jsonify, request, flash, redirect, url_for
#import urllib.request

from app import app, Session
from app.models import User, Event, Run


@app.route('/')
def index():
    return render_template('index.html', username='saurav')

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
    
@app.route('/list')
def listAllRuns():
    files = glob.glob('data/*Run*.gpx')
    
    for file in files:
        gpx_file = open(file, 'r')
        gpx = gpxpy.parse(gpx_file)
 

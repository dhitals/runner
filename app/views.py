import glob
from flask import render_template, jsonify, request, flash, redirect, url_for

from app import app


@app.route('/')
def index():
    return render_template('index.html', username='saurav')

@app.route('/list')
def listAllRuns():
    files = glob.glob('data/*Run*.gpx')
    
    for file in files:
        gpx_file = open(file, 'r')
        gpx = gpxpy.parse(gpx_file)
 

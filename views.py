import glob

from runner import app


@app.route('/')
def index():
    return render_template('Welcome, Runner!')

@app.route('/list')
def listAllRuns():
    files = glob.glob('data/*Run*.gpx')
    
    for file in files:
        gpx_file = open(file, 'r')
        gpx = gpxpy.parse(gpx_file)

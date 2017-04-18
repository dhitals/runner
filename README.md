## Virtual Runner

Run along with a Virtual Runner based on your past

A fun, side-project that aims to predict the pace of your run based on
your running history, your recent mileage, and the current
environmental conditions. 

**Major dependencies (for now):**

* Python 3x (pandas, matplotlib, numpy)
* PostgreSQL + PostGIS
* Flask
* SQLAlchemy
* Folium
* Bokeh
* stravalib
* statmodels
* scikit-learn (maybe?)

**What can be done right now?**

* Import data from GPX files and Strava (using `stravalib`)
* View route of your individual activities
<img src="https://github.com/dhitals/runner/blob/master/app/static/images/example_run.png" width="300">
* Tabulate the monthly/weekly summary of your activities
![Example map of a run.](https://github.com/dhitals/runner/blob/master/app/static/images/example_table.png | width=250)
<img src="https://github.com/dhitals/runner/blob/master/app/static/images/example_table.png" width="300">
* Visualize the monthly/weekly summary of your activities

The visualizations are dynamically served on to the web browser using
`Flask` and `matplotlib`.

**What is under development?**

* Interactive plots using `bokeh`
* Dynamically tracing your runs using `D3.js`
* The prediction part. I am using ARIMA and feeding the residuals into
 a neural net. It is definitely proving to be tricky.


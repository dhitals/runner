## Virtual Runner

Run along with a Virtual Runner based on your past

A fun, side-project that aims to predict the pace of your run based on
your running history, your recent mileage, and the current
environmental conditions. 

**Major dependencies:**

* Python 3x (pandas, matplotlib, numpy)
* PostgreSQL + PostGIS
* Flask
* SQLAlchemy
* Folium
* Bokeh
* stravalib


**What can be done right now?**

* Import data from GPX files and Strava (using `stravalib`)
* Tabulate the monthly/weekly summary of your activities
* Visualize the monthly/weekly summary of your activities

The visualizations are dynamically served on to the web browser using
`Flask` and `matplotlib`.

**What is under development?**

* Interactive plots using `bokeh`
* Dynamically tracing your runs using `D3.js`
* The prediction part, which is the hard stuff. I am using various
  libraries that deal with time-series data, but the predictions are
  still unsatisfactory.

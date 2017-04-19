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
* scikit-learn (maybe? looking for a more flexible neural net library)

___
**Here is the task list:**

- [x] Import data from GPX files and Strava (using `stravalib`)
- [x] View route of your individual activities
  <img src="https://github.com/dhitals/runner/blob/master/app/static/images/example_run.png" width="300">
- [x] Tabulate the monthly/weekly summary of your activities
  <img src="https://github.com/dhitals/runner/blob/master/app/static/images/example_table.png" width="300">
- [x] Visualize the monthly/weekly summary of your activities --- distance,
  time, pace, heartrate, cadence ([example](https://github.com/dhitals/runner/blob/master/app/static/images/example_summary_plot.png))
- [ ] Interactive plots using `bokeh`
- [ ] Dynamically tracing your runs using `D3.js`
- [ ] The prediction part. I am using ARIMA and feeding the residuals into
 a neural net. It is definitely proving to be tricky.

The visualizations are dynamically served on to the web browser using
`Flask` and `matplotlib`.

___
**Disclaimer**: This is a project under active development. Definitely
  not meant for even beta-testing. Yet. More recent development is
  done in Jupyter Notebooks, which I am avoiding uploading as they are
  not amenable to succint version control.

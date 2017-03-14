import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import pint

from app import app, engine, Session
from app.models import User, Activity, Streams

def m_to_mile(x):
    return x * 0.000621371 # meter --> mile

def ns_to_hr(x):
    """ """
    return x * 1e-9 * 0.000277778 * 1e-9 # ns --> s --> hr

def speed_to_pace(speed):
    """ Convert speed (m/s) to pace (MM:SS/mile)"""
    
    u = pint.UnitRegistry()
    
    pace = 1 / (speed * u.meter / u.second).to(u.mile / u.minute)
    pace = ':'.join([str(int(pace.magnitude)),                 
                     str(int((pace.magnitude * 60) % 60)).zfill(2)])
    return pace

def nanosecond_to_hms(t):
    """ Convert time in nanosecond to HH:MM:SS """
    u = pint.UnitRegistry()
    
    # convert from nanoseconds to hour
    t = (t * 1e-9 * u.second).to(u.hour)
    
    hms = [str(int(t.magnitude)),
           str(int(t.magnitude * 60) % 60).zfill(2),
           str(int((t.magnitude * 3600) % 60)).zfill(2)]
    
    t = ':'.join(hms) if t.magnitude >= 1 else ':'.join(hms[1:])
                    
    return t


class summarize(object):
    """ Return a DF w/ a summary of the acitivities grouped by the input parameter 
    
        For e.g., by default, this will return the (average, max, total) values of
        (distance, moving_time, average_speed, average_cadence, average_heartrate) 
        of your activities grouped by (month, week).
    """
 
    def __init__(self, username, type=None, freq=None, fields=None):

        s = Session()

        user_id = s.query(User.id).filter(User.username == username).one()[0]
        type = 'Run' if type is None else type

        q = "SELECT * FROM {0} WHERE user_id={1} AND type='{2}'".format('activities', 
                                                              user_id, 'Run')
        df = pd.read_sql_query(q, engine)
        df.set_index('start_date', inplace=True)
        # change index to specified frequency. DEFAULT: 'M'
        freq = 'M' if freq is None else freq
        df.index = df.index.to_period(freq)
    
        # stats fields to summarize
        if fields is None:
            fields = [  'distance', 'moving_time',
                        'average_speed', 'max_speed',
                        'average_heartrate', 'max_heartrate',
                        'average_cadence', 'max_cadence',
                        'suffer_score', 'total_elevation_gain' ]

        # rearrange the columns in this order
        df = df.reindex(columns=fields)
        
        # drop the rest of the columns
        cols_to_drop = [ cols for cols in df.columns if cols not in fields ]
        df.drop(cols_to_drop, axis=1, inplace=True)
        
        # perform the aggregations
        df = df.groupby(df.index).agg(['count', 'sum', 'mean', 'max'])

        # keep only one version of `count`
        df.insert(0, 'count', df['distance', 'count'])
        df.drop('count', axis=1, level=1, inplace=True)

       # drop MultiIndex -- dropping individual cols is too confusing
        df.columns = [ ('_'.join([c1, c2])) for c1, c2 in \
                        zip(df.columns.get_level_values(level=0), 
                            df.columns.get_level_values(level=1)) ]
        # remove some agg columns that don't make sense. e.g., `sum` of `average_cadence`
        df.drop([ 'average_cadence_sum', 
                  'average_heartrate_sum', 'max_heartrate_sum',
                  'average_speed_sum', 'max_speed_sum',
                  'suffer_score_sum', 'total_elevation_gain_mean'], axis=1, inplace=True)

        self.summary_df = df.sort_index(ascending=False)
        

    def pprint(self):
        """ Pretty print the summary table. """
        df = self.summary_df.copy()
        u = pint.UnitRegistry()
       
        # now, change units and format each column -- !! SLOW !!

        for col in df.columns:
            if 'distance' in col:
                df[col] = df[col].apply(lambda x: (x * u.meter).to(u.mile).magnitude).round(2)
            elif 'time' in col:
                df[col] = df[col].apply(nanosecond_to_hms)
            elif 'speed' in col:
                df[col] = df[col].apply(speed_to_pace)
            elif 'elevation' in col:
                df[col] = df[col].apply(lambda x: (x * u.meter).to(u.feet).magnitude).round(0)
            else:
                df[col] = df[col].round()

        return df

    def plot(self):

        df = self.summary_df.copy()

        fig, ax = plt.subplots(3,2, figsize=(16,10))

        fig, axes = plt.subplots(4,2, figsize=(16,16), sharex=True)

        n, x = len(df), np.arange(n)

        ax = axes[0,0]           
        df.distance_sum.apply(m_to_mile).plot(kind='bar', ax=ax,
                                              label='distance (%s)' %'mile')
        ax = axes[0,1]
        ax.plot(x, df.distance_mean.apply(m_to_mile), 'bo', label='avg distance (%s)' %'miles')
        ax.plot(x, df.distance_max.apply(m_to_mile),  'ro', label='max distance (%s)' %'miles')
        ax.locator_params(nbins=n+1, axis='x')
        ax.set_xticklabels(df.index, rotation=90)
        l = ax.legend(shadow=True)
        frame = l.get_frame()
        frame.set_facecolor('0.0')

        ax = axes[1,0]
        df.moving_time_sum.apply(ns_to_hr).plot(kind='bar', ax=ax, 
                                          label='moving_time (%s)' %'hrs')
        ax = axes[1,1]
        ax.plot(x, df.moving_time_mean.apply(ns_to_hr), 'bo', label='avg time (%s)' %'hrs')
        ax.plot(x, df.moving_time_max.apply(ns_to_hr),  'ro', label='max time (%s)' %'hrs')
        ax.locator_params(nbins=n+1, axis='x')
        ax.set_xticklabels(df.index, rotation=90)
        ax.legend()

        # heartrate
        ax = axes[2,0]
        ax.plot(x, df.average_heartrate_mean, 'bo', label='< avg_heartrate >')
        ax.plot(x, df.average_heartrate_max,  'ro', label='max avg_heartrate')
        ax.locator_params(nbins=n+1, axis='x')
        ax.set_xticklabels(df.index, rotation=90)
        ax.set_ylim([150,200])
        ax.legend()
        
        return

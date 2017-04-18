import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
from io import BytesIO
import base64

from app import app, engine, Session
from app.models import User, Activity, Streams

def m_to_mile(x):
    """ convert distance from meter to miles """
    return x * 0.000621371 # meter --> mile

def ns_to_hms(x, sexagesimal=False):
    """ Convert time units: nanosecond to hour """
    hh = x * 1e-9 * 0.000277778 # ns --> s --> hr

    if sexagesimal:
        hms = [str(int(hh)), 
                str(int(hh * 60) % 60).zfill(2),
                str(int(hh * 2660) % 60).zfill(2)]

        return ':'.join(hms) if hh >= 1 else ':'.join(hms[1:])

    return hh        

def speed_to_pace(x, sexagesimal=False):
    """ convert speed in m/s to pace in min/mile 
        optionally, return sexagesimal pace
    """
    pace = 26.8224 / x # 1 m/s --> min/mile

    if sexagesimal:
        pace = ':'.join([str(int(pace)),
                        str(int((pace * 60) % 60)).zfill(2)])

    return pace


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
                        'average_speed',
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
                  'average_speed_sum', #'max_speed_sum',
                  'suffer_score_sum', 'total_elevation_gain_mean'], axis=1, inplace=True)

        self.summary_df = df.sort_index(ascending=False)
        

    def pprint(self):
        """ Pretty print the summary table. """
        df = self.summary_df.copy()
       
        # now, change units and format each column -- !! SLOW !!

        for col in df.columns:
            if 'distance' in col:
                df[col] = df[col].apply(m_to_mile).round(2)
            elif 'time' in col:
                df[col] = df[col].apply(ns_to_hms, sexagesimal=True)
            elif 'speed' in col:
                df[col] = df[col].apply(speed_to_pace, sexagesimal=True)
            else:
                df[col] = df[col].round()

        return df


    def plot_fill(self, x, ymax, ymean, ax=None, label=None, fill=True):
    
        colors = ('r', 'b')
        stat = ('max', 'total') if 'elevation' in label else ('max', 'avg')

        for y, color, stat in zip((ymax, ymean), colors, stat):
            ax.plot(x, y, color=color, marker='o', 
                    linestyle=None, alpha=0.9, label='%s %s' %(stat, label))
            if fill is True:
                ax.fill_between(x, y, interpolate=True, color=color, alpha=0.5)
        return

    def plot(self, return_b64=False):

        df = self.summary_df.copy()

        fig, axes = plt.subplots(4,2, figsize=(16,16))
        plt.tight_layout()

        # convert `periodIndex` to `timestamp` for plotting
        x = df.index.to_timestamp()
        bar_width = 10 # width of bars in bar graphs

        axes[0,0].bar(x, df.distance_sum.apply(m_to_mile), bar_width,
                      label='total distance (%s)' %'miles')
        self.plot_fill(x, df.distance_max.apply(m_to_mile), 
            df.distance_mean.apply(m_to_mile),
                  ax=axes[0,1], label='distance (%s)' %'miles')

        # moving time - total, average, max
        axes[1,0].bar(x, df.moving_time_sum.apply(ns_to_hms), bar_width,
                      label='total moving_time (%s)' %'hrs')
        self.plot_fill(x, df.moving_time_max.apply(ns_to_hms), 
            df.moving_time_mean.apply(ns_to_hms),
            ax=axes[1,1], label='moving_time (%s)' %'hrs')

        # average speed
        ax = axes[2,0]
        self.plot_fill(x, df.average_speed_max.apply(speed_to_pace), 
                  df.average_speed_mean.apply(speed_to_pace),
                  ax=ax, label='avg_pace', fill=False)
        ax.set_ylim(ax.get_ylim()[::-1])
        ax.set_ylim([11,6])

        # elevation gain
        self.plot_fill(x, df.total_elevation_gain_max, df.total_elevation_gain_sum,
                  ax=axes[2,1], label='elevation gain (m)')
        axes[2,1].set_ylim([0,1000])

        # average heartrate
        self.plot_fill(x, df.average_heartrate_max, df.average_heartrate_mean,
                  ax=axes[3,0], label='avg_heartrate', fill=False)
        axes[3,0].set_ylim([150,200])

        # average cadence
        self.plot_fill(x, df.average_cadence_mean, df.average_cadence_max,
                  ax=axes[3,1], label='avg_cadence', fill=False)
        axes[3,1].set_ylim([75,90])

        for ax in axes.reshape(-1): 
            # format the xticknames
            ax.locator_params(nbins=len(df)+1, axis='x')
            ax.xaxis.set_tick_params(reset=True)
            ax.xaxis.set_minor_locator(mdates.MonthLocator())
            ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('\n%Y'))

            ax.legend()
                
        if return_b64:
            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0) # go to the beginning

            return base64.b64encode(img.getvalue()).decode('utf8')
        else:
            return

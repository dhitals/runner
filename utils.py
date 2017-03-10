import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import pint

from app import app, engine, Session
from app.models import User, Activity, Streams

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
 
    def __init__(self, username, type=None, freq=None):

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
    
        # rearrange the columns in this order
        self.summary_cols = ( 'distance', 'moving_time', 'speed', 'max_speed'
                              'average_heartrate', 'max_heartrate',
                              'average_cadence', 'max_cadence',
                              'suffer_score', 'total_elevation_gain' )
   
        # drop the rest of the columns
        cols_to_drop = [ cols for cols in df.columns if cols not in self.summary_cols ]
        df.drop(cols_to_drop, axis=1, inplace=True)
        
        # perform the aggregations
        self.summary_df = df.groupby(df.index).agg(['count', 'mean', 'sum', 'max'])#.reindex(columns=self.summary_cols)
            
        # rearrange the order of the columns
        #df = df.reindex(columns=self.summary_cols)

        return

    def pprint(self):
        """ Pretty print the summary table. 
        This is slow likely b/c each column is operated on individually in a FOR loop 
        """
        df = self.summary_df.copy()
        u = pint.UnitRegistry()
       
        # now, change units and format each column
        for col in df.columns:
            if 'n_activities' in col:
                df[col] = df[col].map('{:.0f}'.format)
            elif 'distance' in col:
                df[col] = df[col].apply(lambda x: (x * u.meter).to(u.mile)).map('{:.2f}'.format)
            elif 'elev' in col:
                df[col] = df[col].apply(lambda x: (x * u.meter).to(u.feet)).map('{:.0f}'.format)
            elif 'speed' in col:
                df[col] = df[col].map(speed_to_pace)
            elif 'time' in col:
                df[col] = df[col].map(nanosecond_to_hms)
            else:
                df[col] = df[col].map('{:.2f}'.format)
                
        return df

    def plot(self):

        df = self.summary_df.copy()

        fig, ax = plt.subplots(3,2, figsize=(16,10))


        
        #ax[0,0].plot(df.index, df.total_distance, marker='o', color='b', 
        #    label='total_distance')
        df.plot.scatter(y='total_distance', ax=ax[0,0])
        df.plot(y='average_distance', kind='bar', ax=ax[0,1])
        df.plot(y='max_distance', kind='bar', ax=ax[0,1])
        
        df.plot(y='total_moving_time', kind='bar', ax=ax[1,0])
        df.plot(y='average_moving_time', kind='bar', ax=ax[1,1])
        df.plot(y='max_moving_time', kind='bar', ax=ax[1,1])

        df.plot(y='average_heartrate', kind='bar', ax=ax[2,0])
        df.plot(y='max_average_heartrate', kind='bar', ax=ax[2,0])

        df.plot(y='average_cadence', kind='bar', ax=ax[2,1])
        df.plot(y='max_average_cadence', kind='bar', ax=ax[2,1])
        
        return

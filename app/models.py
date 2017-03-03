import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, Interval, Float, ForeignKey, String
from geoalchemy2 import Geometry
from app import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(10), unique=True, nullable=False)
    email    = Column(String(25), unique=True, nullable=False)
    fname    = Column(String)
    lname    = Column(String)
    password = Column(String(25))
    strava_id = Column(Integer)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, username, email, fname, lname, password):
        self.username = username
        self.email = email
        self.fname = fname
        self.lname = lname
        self.password = password
        
    def __repr__(self):
        return "<User(name='%s', fullname='%s %s', email='%s')>" % (
            self.username, self.fname, self.lname, self.email)


class Activity(Base):
    __tablename__ = 'activity'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    athlete_count = Column(Integer)
    average_cadence = Column(Float)
    average_heartrate = Column(Float)
    average_speed = Column(Float)
    distance = Column(Float)
    elapsed_time = Column(Interval)
    elev_high = Column(Float)
    elev_low = Column(Float)
    end_latlng = Column(String(32))
    external_id = Column(String(32))
    gear_id = Column(String(12))
    has_heartrate = Column(Boolean)
    location_city = Column(String(32))
    location_country = Column(String(32))
    location_state = Column(String(32))
    manual = Column(Boolean)
    max_heartrate = Column(Float)
    max_speed = Column(Float)
    moving_time = Column(Interval)
    name = Column(String(32))
    pr_count = Column(Integer)
    start_date = Column(DateTime)
    start_date_local = Column(DateTime)
    start_latitude = Column(Float)
    start_latlng = Column(String(32))
    start_longitude = Column(Float)
    strava_id = Column(Integer) 
    suffer_score = Column(Integer)
    timezone = Column(String(32))
    total_elevation_gain = Column(Float)
    type = Column(String)
    upload_id = Column(String)
    workout_type = Column(String)

    def __repr__(self):
        return "<Event(id='%s', datetime='%s', name='%s')>" % (
            self.id, self.start_time, self.name)


    
class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    datetime = Column(DateTime)
    run_type = Column(String)
    distance = Column(Float)
    duration = Column(Float)
    avg_speed = Column(Float)
    max_speed = Column(Float)
    avg_pace = Column(String)
    avg_heartrate = Column(String)
    avg_cadence = Column(String)
    source = Column(String)
    shoes = Column(String)
    filename = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return "<Event(id='%s', datetime='%s', name='%s')>" % (
            self.id, self.start_time, self.name)

class Run(Base):
    __tablename__ = 'runs'

    time = Column(DateTime, primary_key=True)
    #point = Column(Geometry(geometry_type='Point', srid=4326))
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    speed = Column(Float)
    heartrate  = Column(Float)
    cadence = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    event_id = Column(Integer, ForeignKey('events.id'))

    def __repr__(self):
        return "<Event(time='%s'')>" % (
            self.time)

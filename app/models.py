import datetime
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, Interval, Float, ForeignKey, String
from geoalchemy2 import Geometry
from app import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(10), unique=True, nullable=False)
    email    = Column(String(25), unique=True, nullable=True)
    fname    = Column(String)
    lname    = Column(String)
    password = Column(String(25))
    strava_id = Column(Integer)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, username, email, fname, lname, password, strava_id):
        self.username = username
        self.email = email
        self.fname = fname
        self.lname = lname
        self.password = password
        self.strava_id = strava_id
        
    def __repr__(self):
        return "<User(name='%s', fullname='%s %s', email='%s')>" % (
            self.username, self.fname, self.lname, self.email)


class Activity(Base):
    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True)
    athlete_count = Column(Integer)
    average_cadence = Column(Float)
    average_heartrate = Column(Float)
    average_speed = Column(Float)
    distance = Column(Float)
    elapsed_time = Column(BigInteger)
    elev_high = Column(Float)
    elev_low = Column(Float)
    end_latlng = Column(String(64))
    external_id = Column(String(64))
    gear_id = Column(String(12))
    has_heartrate = Column(Boolean)
    location_city = Column(String(64))
    location_country = Column(String(64))
    location_state = Column(String(64))
    manual = Column(Boolean)
    max_heartrate = Column(Float)
    max_speed = Column(Float)
    moving_time = Column(BigInteger)
    name = Column(String(64))
    pr_count = Column(Integer)
    start_date = Column(DateTime)
    start_date_local = Column(DateTime)
    start_latitude = Column(Float)
    start_latlng = Column(String(64))
    start_longitude = Column(Float)
    strava_id = Column(Integer, unique=True) 
    suffer_score = Column(Integer)
    timezone = Column(String(64))
    total_elevation_gain = Column(Float)
    type = Column(String)
    upload_id = Column(String, unique=True)
    workout_type = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return "<Event(id='%s', datetime='%s', name='%s')>" % (
            self.id, self.start_date, self.name)


class Streams(Base):
    __tablename__ = 'streams'

    id = Column(Integer, primary_key=True)
    time = Column(Integer)
    #point = Column(Geometry(geometry_type='Point', srid=4326))
    distance = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    latlng = Column(String(64))
    altitude = Column(Float)
    velocity_smooth = Column(Float)
    heartrate  = Column(Float)
    cadence = Column(Float)
    moving = Column(Boolean)
    temp = Column(Float)
    grade_smooth = Column(Float)
    humidity = Column(Float)
    windSpeed = Column(Float)
    windDir = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    activity_id = Column(Integer, ForeignKey('activities.id'))

    def __repr__(self):
        return "<Event(time='%s'')>" % (
            self.time)

    
# class Event(Base):
#     __tablename__ = 'events'

#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     datetime = Column(DateTime)
#     run_type = Column(String)
#     distance = Column(Float)
#     duration = Column(Float)
#     avg_speed = Column(Float)
#     max_speed = Column(Float)
#     avg_pace = Column(String)
#     avg_heartrate = Column(String)
#     avg_cadence = Column(String)
#     source = Column(String)
#     shoes = Column(String)
#     filename = Column(String)
#     user_id = Column(Integer, ForeignKey('users.id'))

#     def __repr__(self):
#         return "<Activity(id='%s', datetime='%s', name='%s')>" % (
#             self.id, self.start_time, self.name)

# class Run(Base):
#     __tablename__ = 'runs'

#     time = Column(DateTime, primary_key=True)
#     #point = Column(Geometry(geometry_type='Point', srid=4326))
#     latitude = Column(Float)
#     longitude = Column(Float)
#     altitude = Column(Float)
#     speed = Column(Float)
#     heartrate  = Column(Float)
#     cadence = Column(Float)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     event_id = Column(Integer, ForeignKey('events.id'))

#     def __repr__(self):
#         return "<Event(time='%s'')>" % (
#             self.time)
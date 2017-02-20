import datetime
from sqlalchemy import Column, DateTime, Integer, Float, ForeignKey, String
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


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    datetime = Column (DateTime)
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
    elevation = Column(Float)
    speed = Column(Float)
    heartrate  = Column(Float)
    cadence = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    event_id = Column(Integer, ForeignKey('events.id'))

    def __repr__(self):
        return "<Event(time='%s'')>" % (
            self.time)

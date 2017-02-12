import datetime
from sqlalchemy import Column, DateTime, Integer, Float, String
from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String)
    fname = Column(db.String)
    lname = Column(db.String)
    password = Column(db.String)
    created_date = Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<User(name='%s', fullname='%s %s', password='%s')>" % (
            self.name, self.fname, self.lname, self.password)

class Run(db.Model):
    __tablename__ = 'runs'

    time = Column(db.DateTime, primary_key=True) # start datetime
    point = Column(db.Geometry('Point', srid=4326))
    elevation = Column(db.Float)
    heartRate  = Column(db.Float)
    cadence = Column(db.Float)

class Events(db.Model):
    __tablename__ = 'events'
        
    start_time = Column(db.DateTime, primary_key=True) # start datetime
    name = Column(db.String)
    run_type = Column(db.String)
    length = Column(db.Float)
    avg_speed = Column(db.Float)
    max_speed = Column(db.Float)
    avg_pace = Column(db.String)
    avg_heartRate = Column(db.String)
    avg_cadence = Column(db.String)
    distance = Column(db.Float)
    source = Column(db.String)
    year = Column(db.Integer)
    month = Column(db.Integer)
    week = Column(db.Integer)
    filename = Column(db.String)

import datetime
from sqlalchemy import Column, Datetime, Integer, Float, String
from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    
class Run(db.Model):
    __tablename__ = 'runs'
    
    id = Column(db.Integer, primary_key=True)
    point = Column(Geometry('Point', srid=4326))
    datetime = Column(DateTime)
    value = Column(Float)

class allRuns(db.Model):
    datetime = Column(Datetime, primary_key=True) # start datetime
    name = Column(String)
    speed = Column(Float)
    pace = Column(String)
    distance = Column(Float)
    source = Column(String)
    

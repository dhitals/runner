from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import psycopg2 as pg

app = Flask(__name__)

app.config.from_object('config.DevelopmentConfig')
# app.config.from_envvar('~/runner.cfg', silent=True)

db = SQLAlchemy(app)
db = pg.connect(app.config['DATABASE_URI'])

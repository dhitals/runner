import sys
from flask import Flask, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import psycopg2 as pg

#app = Flask(__name__)
from app import app, db

#app.config.from_object('config')
#db = SQLAlchemy(app)
#print(dir(app.config))


if __name__ == '__main__':

    if "createdb" in sys.argv:
        dbname = 'runner'

        # connec to default db
        try:
            conn = connect(dbname='postgres', user='saurav', host='localhost', password='saurav')
        except:
            print('I am unable to connect to database.')

        # add exception if DB already exists

        # create db
        try:
            cur = conn.cursor()
            conn.set_isolation_level(0)
            cur.execute("""CREATE DATABASE runner""")    
        except:
            print('I cannot create new database')

    elif "importdb" in sys.argv:
        #with app.app_context():
        print('Importing data')
    else:
        app.run()

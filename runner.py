import sys
#from flask import Flask, request, render_template, session, flash
#from flask_sqlalchemy import SQLAlchemy
#import psycopg2 as pg
from app import app, db
from data_keeper import data_keeper


if __name__ == '__main__':

    recreate = True if "createdb" in sys.argv else False
    
    if "importdb" in sys.argv:
        print('Importing data ...')
        dk = datakeeper(recrete_if_exists=recreate)
    else:
        app.run()

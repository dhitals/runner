from flask import Flask
import views
#import pg

app = Flask(__name__)
app.config.from_pyfile('runner.cfg')
print(dir(app.config))

db = pg.connect(app.config['APP_NAME'], \
     app.config['PG_DB_HOST'], \
     app.config['PG_DB_PORT'], \
     None, None, \
     app.config['PG_DB_USERNAME'], \
     app.config['PG_DB_PASSWORD'] )

if __name__ == '__main__':

    if "importdb" in sys.argv:
        #with app.app_context():
        print('Importing data')
    else:
        app.run()

import os
from flask import *
from models.sqlmodel import db
from utils import readConf, uuidGen
from routes import mainBluePrint
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    app = Flask(__name__)
    try:
        if config_name == "default":
            db_uri = f"mysql+pymysql://{readConf('database', 'username')}:{readConf('database', 'password')}@" \
                     f"{readConf('database', 'host')}:{readConf('database', 'port')}/{readConf('database', 'dbname')}"
        elif config_name == "testing":
            db_uri = f"mysql+pymysql://{readConf('database', 'username')}:{readConf('database', 'password')}@" \
                     f"{readConf('database', 'host')}:{readConf('database', 'port')}/testDB"
            app.config['TESTING'] = True
        else:
            print("Unknown action.")
            return -1
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        app.config['SECRET_KEY'] = uuidGen()
    except Exception as e:
        logger.error(f"Failed to create app: {e}")
        raise

    db.init_app(app)
    app.register_blueprint(mainBluePrint)

    if config_name == "testing":
        with app.app_context():
            db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

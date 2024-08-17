from flask import Flask
from models.sqlmodel import db
from actions.extraact import uuidGen
from actions.utils import readConf
from routes import register_routes
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
        else:
            print("Unknown action.")
            return -1
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = uuidGen()
        app.config['TIMEZONE'] = readConf("systemConfig", "timezone")
    except Exception as e:
        logger.error(f"Failed to create app: {e}")
        raise

    db.init_app(app)
    register_routes(app)

    if config_name == "testing":
        with app.app_context():
            db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

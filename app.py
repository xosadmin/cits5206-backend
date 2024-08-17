from flask import Flask
from models.sqlmodel import db
from utils import readConf
from routes import register_routes
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from sqlalchemy import inspect

def create_app(config_name='default'):
    app = Flask(__name__)
    try:
        db_uri = f"mysql+pymysql://{readConf('database', 'username')}:{readConf('database', 'password')}@" \
                 f"{readConf('database', 'host')}:{readConf('database', 'port')}/{readConf('database', 'dbname')}"
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'supersecretkey'
        app.config['TIMEZONE'] = readConf("systemConfig", "timezone")
    except Exception as e:
        logger.error(f"Failed to create app: {e}")
        raise

    db.init_app(app)
    register_routes(app)

    # Initialize the database
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

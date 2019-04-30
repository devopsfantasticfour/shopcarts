"""
Package: app
Package for the application models and services
This module also sets up the logging to be used with gunicorn
"""
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import ibm_db_sa
from app.vcap_services import get_database_uri
# Create Flask application
app = Flask(__name__)

# We use db2 as persistence database
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'please, tell nobody... Shhhh'
app.config['LOGGING_LEVEL'] = logging.INFO

# Initialize SQLAlchemy
db = SQLAlchemy(app)

from app import service, model

# Set up logging for production
print 'Setting up logging for {}...'.format(__name__)
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

app.logger.info('Logging established')

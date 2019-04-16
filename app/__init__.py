
"""
Package: app

Package for the application models and services
This module also sets up the logging to be used with gunicorn
"""
import logging
import os
from environs import Env
from flask import Flask

# Create Flask application
app = Flask(__name__)

from . import service

# base directory of flask app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # up one directory
# root directory of project
ROOT_DIR = os.path.dirname(BASE_DIR)  # up one more directory

env = Env()

# read env file if it exists
try:
    env.read_env(os.path.join(ROOT_DIR, '.env'))
except OSError:
    pass

DB_HOST = env('DB_HOST')
DB_NAME = env('DB_NAME')
DB_USER = env('DB_USER')
DB_PASSWORD = env('DB_PASSWORD')

SECRET_KEY = env('SECRET_KEY', 'Please, tell nobody... Shhhhh')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['LOGGING_LEVEL'] = logging.INFO

# Create Postgres connection string
postgres_connection = 'postgres://{user}:{pw}@{host}/{db}'.format(user=DB_USER, pw=DB_PASSWORD, host=DB_HOST,
                                                                  db=DB_NAME)
app.config['SQLALCHEMY_DATABASE_URI'] = postgres_connection

# Set up logging for production
print ('Setting up logging for {}...'.format(__name__))
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    else:
        service.initialize_logging()
    service.init_db()  # make our sqlalchemy tables

app.logger.info('Logging established')

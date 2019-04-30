import os
import json
import logging

def get_database_uri():
    """
    Initialized DB2 database connection
    This method will work in the following conditions:
      1) With DATABASE_URI as an environment variable
      2) In Bluemix with DB2 bound through VCAP_SERVICES
      3) With PostgreSQL running on the local server as with Travis CI
    """
    database_uri = None
    if 'DATABASE_URI' in os.environ:
        # Get the credentials from DATABASE_URI
        logging.info("Using DATABASE_URI...")
        database_uri = os.environ['DATABASE_URI']
    elif 'VCAP_SERVICES' in os.environ:
        # Get the credentials from the Bluemix environment
        services = json.loads(os.environ['VCAP_SERVICES'])
        database_uri = services['dashDB For Transactions'][0]['credentials']["uri"]
    else:
        database_uri = "postgres://postgres:postgres@localhost:5432/postgres"

    return database_uri
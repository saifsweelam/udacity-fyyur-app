import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True


# Avoid Deprecation Warning
SQLALCHEMY_TRACK_MODIFICATIONS = False


# TODO: DONE
# Connect to the database
# DATABASE URI IMPLEMENTED
# Username: postgres
# Password: saif7711
# DB Name: fyyur
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:saif7711@localhost:5432/fyyur'

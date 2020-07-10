#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
from datetime import datetime
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
# Import Migrate Object
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: DONE
# CONNECTED TO DATABASE WITH URI IN "config.py"

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Show(db.Model):
    __tablename__ = 'show'

    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime)
    venue = db.relationship("Venue", back_populates="artists")
    artist = db.relationship("Artist", back_populates="venues")


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String())
    artists = db.relationship("Show", back_populates="venue")

    # TODO: DONE
    # Added 'genres' & 'website' & 'seeking_talent'
    # & 'seeking description' columns


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String())
    venues = db.relationship("Show", back_populates="artist")

    # TODO: DONE
    # Added 'website' & 'seeking_talent' &
    # 'seeking description' columns

# TODO: DONE
# Implemented Show and Artist models, and completed
# all model relationships and properties.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: DONE
    # replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per venue.
    cities = db.session.query(Venue.city, func.count(
        Venue.name)).group_by(Venue.city).all()
    data = [{
        "city": city[0],
        "state": Venue.query.filter_by(city=city[0]).first().state,
        "venues": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.artists))),
        } for venue in Venue.query.filter_by(city=city[0]).all()]
    } for city in cities]
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: DONE
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    search_term = request.form.get('search_term', '').lower()
    results = [x for x in Venue.query.all() if search_term in x.name.lower()]
    response = {
        "count": len(results),
        "data": [{
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), result.artists))),
        } for result in results]
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    try:
        # shows the venue page with the given venue_id
        # TODO: DONE
        # replace with real venue data from the venues table, using venue_id
        venue = Venue.query.get(venue_id)
        shows = venue.artists
        past_shows = list(
            filter(lambda x: x.start_time < datetime.now(), shows))
        upcoming_shows = list(
            filter(lambda x: x.start_time > datetime.now(), shows))

        data = {
            "past_shows": [{
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
            } for show in past_shows],
            "upcoming_shows": [{
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
            } for show in upcoming_shows],
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }
        data.update(venue.__dict__)
        data['genres'] = data['genres'].split(', ')
        return render_template('pages/show_venue.html', venue=data)
    except:
        return abort(404)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO:DONE insert form data as a new Venue record in the db, instead
    # TODO:DONE modify data to be the data object returned from db insertion
    try:
        venue = Venue(
            name=request.form.get('name'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            address=request.form.get('address'),
            phone=request.form.get('phone'),
            genres=', '.join(request.form.getlist('genres')),
            image_link=request.form.get('image_link'),
            facebook_link=request.form.get('facebook_link'),
            website=request.form.get('website'),
            seeking_talent=not not request.form.get('seeking_description', '')
        )
        if venue.seeking_talent:
            venue.seeking_description = request.form.get('seeking_description')
        name = venue.name
        db.session.add(venue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + name + ' was successfully listed!')
    except Exception as e:
        # TODO: DONE
        # on unsuccessful db insert, flash an error instead.
        print(e)
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        # TODO: Complete this endpoint for taking a venue_id, and using
        # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
        Show.query.filter_by(venue_id=venue_id).delete()
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()

        # BONUS CHALLENGE: DONE
        # Implement a button to delete a Venue on a Venue Page
        return jsonify({
            'state': "Success"
        })
    except:
        db.session.rollback()
        return abort(500)

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: DONE
    # replace with real data returned from querying the database
    data = [artist.__dict__ for artist in Artist.query.all()]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: DONE
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    search_term = request.form.get('search_term', '').lower()
    results = [x for x in Artist.query.all() if search_term in x.name.lower()]
    response = {
        "count": len(results),
        "data": [{
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), result.venues))),
        } for result in results]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: DONE
    # replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)
    shows = artist.venues
    past_shows = list(filter(lambda x: x.start_time < datetime.now(), shows))
    upcoming_shows = list(
        filter(lambda x: x.start_time > datetime.now(), shows))

    data = {
        "past_shows": [{
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        } for show in past_shows],
        "upcoming_shows": [{
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        } for show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    data.update(artist.__dict__)
    data['genres'] = data['genres'].split(', ')
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    try:
        # TODO: DONE
        # populate form with fields from artist with ID <artist_id>
        artist = Artist.query.get(artist_id)
        form = ArtistForm(
            name=artist.name,
            city=artist.city,
            state=artist.state,
            phone=artist.phone,
            genres=artist.genres.split(', '),
            website=artist.website,
            facebook_link=artist.facebook_link,
            image_link=artist.image_link,
            seeking_description=artist.seeking_description
        )
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    except:
        return abort(404)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        # TODO: DONE
        # take values from the form submitted, and update existing
        # artist record with ID <artist_id> using the new attributes
        artist = Artist.query.get(artist_id)
        artist.name = request.form.get('name')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.genres = ', '.join(request.form.getlist('genres'))
        artist.website = request.form.get('website')
        artist.facebook_link = request.form.get('facebook_link')
        artist.image_link = request.form.get('image_link')
        artist.seeking_venue = not not request.form.get('seeking_description', '')
        artist.seeking_description = request.form.get(
            'seeking_description') if artist.seeking_venue else None
        db.session.commit()

        return redirect(url_for('show_artist', artist_id=artist_id))
    except:
        db.session.rollback()
        return abort(500)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # TODO: DONE
    # populate form with values from venue with ID <venue_id>
    try:
        venue = Venue.query.get(venue_id)
        form = VenueForm(
            name=venue.name,
            city=venue.city,
            state=venue.state,
            address=venue.address,
            phone=venue.phone,
            genres=venue.genres.split(', '),
            website=venue.website,
            facebook_link=venue.facebook_link,
            image_link=venue.image_link,
            seeking_description=venue.seeking_description
        )
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    except:
        return abort(404)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        # TODO: DONE
        # take values from the form submitted, and update existing
        # venue record with ID <venue_id> using the new attributes
        venue = Venue.query.get(venue_id)
        venue.name = request.form.get('name')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        venue.genres = ', '.join(request.form.getlist('genres'))
        venue.website = request.form.get('website')
        venue.facebook_link = request.form.get('facebook_link')
        venue.image_link = request.form.get('image_link')
        venue.seeking_talent = not not request.form.get('seeking_description', '')
        venue.seeking_description = request.form.get(
            'seeking_description') if venue.seeking_talent else None
        db.session.commit()
        return redirect(url_for('show_venue', venue_id=venue_id))

    except:
        db.session.rollback()
        return abort(500)

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: DONE
    # insert form data as a new Venue record in the db
    try:
        artist = Artist(
            name=request.form.get('name'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            phone=request.form.get('phone'),
            genres=', '.join(request.form.getlist('genres')),
            image_link=request.form.get('image_link'),
            facebook_link=request.form.get('facebook_link'),
            website=request.form.get('website'),
            seeking_venue=not not request.form.get('seeking_description', '')
        )
        if artist.seeking_venue:
            artist.seeking_description = request.form.get(
                'seeking_description')
        name = artist.name
        db.session.add(artist)
        db.session.commit()

        # TODO: DONE
        # modify data to be the data object returned from db insertion
        # on successful db insert, flash success
        flash('Artist ' + name + ' was successfully listed!')
    except Exception as e:
        # TODO: DONE
        # on unsuccessful db insert, flash an error instead.
        print(e)
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: DONE
    # replace with real venues data.
    shows = Show.query.all()
    data = [{
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    } for show in shows]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: DONE
    # insert form data as a new Show record in the db
    try:
        show = Show(
            start_time=request.form.get('start_time', datetime.now()),
            artist=Artist.query.get(int(request.form.get('artist_id'))),
            venue=Venue.query.get(int(request.form.get('venue_id')))
        )
        db.session.add(show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception as e:
        # TODO: DONE
        # on unsuccessful db insert, flash an error instead.
        print(e)
        flash('An error occurred. Show could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

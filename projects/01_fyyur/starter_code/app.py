#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import func
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# DONE: connect to a local postgresql database DONE

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# I had problems with assosiate tabe I couldn't make any query with it since it throw exptions 
# What I made in one to many for one artist has many shows and one venue has many show
class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    artists = db.relationship('Show', backref=db.backref('Venue', lazy=True))

    # DONE: implement any missing fields, as a database migration using Flask-Migrate DONE

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    venues = db.relationship('Show', backref=db.backref('Artist', lazy=True))

    # DONE: implement any missing fields, as a database migration using Flask-Migrate DONE

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration. DONE

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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
  # DONE: replace with real venues data. DONE
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  cities = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data =[]
  #after getting all data about the venues grouped by cities and states this loop will orgnize the data 
  for city in cities:
    venues = Venue.query.filter_by(city=city.city).filter_by(state=city.state).all()
    vdata = []
    #this loop will fill each city with its venues
    for venue in venues:
      show_data = Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all()
      num_upcoming_shows = len(show_data)
      vdata.append({
        "id": venue.id,
        "name": venue.name, 
        "num_upcoming_shows": num_upcoming_shows
      })
    data.append({
      "city": city.city,
      "state": city.state, 
      "venues": vdata
    })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.DONE
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term','')
  results = Venue.query.filter(Venue.name.like(f'%{search_term}%')).all()
  count = len(results)
  data =[]
  #orgnizing the data
  for result in results:
    show_data = Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all()
    num_upcoming_shows = len(show_data)
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": num_upcoming_shows
    })  
  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id DONE
  venue = Venue.query.get(venue_id)

  upcoming_shows_data = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []

  past_shows_data = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []
  #orgnizing the data
  for show in upcoming_shows_data:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")    
    })
  #orgnizing the data
  for show in past_shows_data:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  error = False
  data = request.form
  try: 
    name = data['name']
    city = data['city']
    state = data['state']
    address = data['address']
    phone = data['phone']
    image_link = data['image_link']
    facebook_link = data['facebook_link']
    genres = data.getlist('genres')
    website = data['website']
    seeking_talent = True if 'seeking_talent' in data else False 
    seeking_description = data['seeking_description']

    venue = Venue(name=name, 
                  city=city, 
                  state=state, 
                  address=address, 
                  phone=phone,  
                  facebook_link=facebook_link, 
                  image_link=image_link, 
                  website=website, 
                  genres=genres,
                  seeking_talent=seeking_talent, 
                  seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()

  if error: 
    flash('An error occurred. Venue ' + data['name']+ ' could not be listed.')
  if not error:
    flash('Venue ' + data['name'] + ' was successfully listed!')
  # on successful db insert, flash success
  # DONE: on unsuccessful db insert, flash an error instead. DONE
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using DONE
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error: 
    flash(f'An error has occurred')
  if not error: 
    flash(f'Venue successfully deleted.')
  return render_template('pages/home.html')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive. DONE
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')
  results = Artist.query.filter(Artist.name.like(f'%{search_term}%')).all()
  count = len(results)
  data = []
  #orgnizing the data
  for result in results:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(Show.query.filter(Show.artist_id == result.id).filter(Show.start_time > datetime.now()).all()),
    })
  
  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  past_shows_data = Show.query.join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []

  upcoming_shows_data = Show.query.join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []
  #orgnizing the data
  for show in past_shows_data:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_image_link": show.Venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  #orgnizing the data  
  for show in upcoming_shows_data:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_image_link": show.Venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "image_link": artist.image_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
 
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website.data = artist.website
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing DONE
  # artist record with ID <artist_id> using the new attributes
  error = False  
  artist = Artist.query.get(artist_id)
  data = request.form
  try: 
    artist.name = data['name']
    artist.city = data['city']
    artist.state = data['state']
    artist.phone = data['phone']
    artist.genres = data.getlist('genres')
    artist.image_link = data['image_link']
    artist.facebook_link = data['facebook_link']
    artist.website = data['website']
    artist.seeking_venue = True if 'seeking_venue' in data else False 
    artist.seeking_description = data['seeking_description']
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('An error has occurred')
  if not error: 
    flash('Artist successfully updated')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.address.data = venue.address
  form.genres.data = venue.genres
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.website.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing DONE
  # venue record with ID <venue_id> using the new attributes
  error = False  
  venue = Venue.query.get(venue_id)
  data = request.form
  try: 
    venue.name = data['name']
    venue.city = data['city']
    venue.state = data['state']
    venue.address = data['address']
    venue.phone = data['phone']
    venue.genres = data.getlist('genres')
    venue.image_link = data['image_link']
    venue.facebook_link = data['facebook_link']
    venue.website = data['website']
    venue.seeking_talent = True if 'seeking_talent' in data else False 
    venue.seeking_description = data['seeking_description']

    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash(f'An error occurred')
  if not error: 
    flash(f'Venue successfully updated')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Venue record in the db, instead DONE
  # DONE: modify data to be the data object returned from db insertion DONE
  error = False
  data = request.form
  try: 
    name = data['name']
    city = data['city']
    state = data['state']
    phone = data['phone']
    genres = data.getlist('genres'),
    facebook_link = data['facebook_link']
    image_link = data['image_link']
    website = data['website']
    seeking_venue = True if 'seeking_venue' in data else False
    seeking_description = data['seeking_description']

    artist = Artist(name=name, 
                    city=city, 
                    state=state,
                    phone=phone, 
                    genres=genres, 
                    facebook_link=facebook_link, 
                    image_link=image_link, 
                    website=website, 
                    seeking_venue=seeking_venue, 
                    seeking_description=seeking_description)

    db.session.add(artist)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Artist ' + data['name']+ ' could not be listed.')
  if not error: 
    flash('Artist ' + data['name'] + ' was successfully listed!')
  # on successful db insert, flash success
  # DONE: on unsuccessful db insert, flash an error instead. DONE
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.join(Artist).join(Venue).all()

  data = []
  for show in shows: 
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name, 
      "artist_image_link": show.Artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  error = False
  data = request.form
  print(data)
  try: 
    artist_id = data['artist_id']
    venue_id = data['venue_id']
    start_time = data['start_time']

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    print(show)

    db.session.add(show)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Show could not be listed.')
  if not error: 
    flash('Show was successfully listed')
  # on successful db insert, flash success
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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

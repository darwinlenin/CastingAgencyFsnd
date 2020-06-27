import os
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort, session
from flask_moment import Moment
from models import setup_db, Actor, Movie, ComeOut
from sqlalchemy import exc
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
from operator import itemgetter
import sys
from flask_cors import CORS, cross_origin
from datetime import datetime
from auth import AuthError, requires_auth

from functools import wraps
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
import http


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  app.secret_key = 'gVDJ63B0mhFrQFXy4zMzqB65zuzh-58VcaDVBep_p7UVTlM6h-ghQ-Ul4SQg_Xnr'
  app.debug = True
  setup_db(app)
  CORS(app)

  return app

app = create_app()

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id='fEDJSnB6Gb57nXJWzdTakt1x1N39x6EU',
    client_secret='gVDJ63B0mhFrQFXy4zMzqB65zuzh-58VcaDVBep_p7UVTlM6h-ghQ-Ul4SQg_Xnr',
    api_base_url='https://'+os.environ['AUTH0_DOMAIN'],
    access_token_url='https://'+os.environ['AUTH0_DOMAIN']+'/oauth/token',
    authorize_url='https://'+os.environ['AUTH0_DOMAIN']+'/authorize',
    client_kwargs={
        'scope': 'delete:movies get:movies get:actors post:actors post:movies get:comeouts post:comeouts',
    },
)




# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement ComeOut and Actor models, and complete all model relationships and properties, as a database migration.

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
@cross_origin(headers=['Content-Type', 'Authorization'])
def index():
  return render_template('pages/home.html')


#  Movies
#  ----------------------------------------------------------------

@app.route('/movies')
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth('get:movies')
def movies():
  # TODO: replace with real Movies data.
  #       num_ComeOuts should be aggregated based on number of upcoming ComeOuts per Movie.
  
  data = []
  movies = []

  movie_list = Movie.query.with_entities(
      Movie.city, Movie.state).order_by('id').all()
  #print('Movie_list!', Movie_list)

  for movie_lis in movie_list:
    if (not function(data, movie_lis.city,"city")):
      movies = []
      movie_direction_list = Movie.query.with_entities(
            Movie.id, Movie.city, Movie.name, Movie.title, Movie.release_date, Movie.upcoming_comeouts_count).filter_by(city=movie_lis.city).order_by('id').all()
      
      for movie_lis_direction in movie_direction_list:
        if (not function(movies, movie_lis_direction.id, "id")):
          movies.append({"id": movie_lis_direction.id, "name": movie_lis_direction.name,
                      "title": movie_lis_direction.title,
                      "release_date": movie_lis_direction.release_date,
                      "num_upcoming_comeouts": movie_lis_direction.upcoming_comeouts_count})
      
      data.append({"city": movie_lis.city,
                    "state": movie_lis.state, "movies": movies})
    
  #print('data!', data)

  return render_template('pages/movies.html', areas=data);

def function(json_object, name, key):
    for dict in json_object:
        if dict[key] == name:
            return True

@app.route('/movies/search', methods=['POST'])
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth('post:movies')
def search_movies():
  # TODO: implement search on Actors with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  search = "%"+search_term+"%"
  movie_list = Movie.query.with_entities(Movie.id, Movie.name, Movie.upcoming_comeouts_count).filter(Movie.name.ilike(search)).order_by('id').all()
  count = Movie.query.with_entities(
      Movie.id, Movie.name, Movie.upcoming_comeouts_count).filter(Movie.name.ilike(search)).count()
  data = []
  for movie in movie_list:
    data.append({"id": movie.id, "name": movie.name,
                 "num_upcoming_comeouts": movie.upcoming_comeouts_count})
  response = {"count": count, "data": movie_list}

  return render_template('pages/search_movies.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/movies/<int:movie_id>')
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth('get:movies')
def show_movie(movie_id):
  # ComeOuts the Movie page with the given movie_id
  # TODO: replace with real Movie data from the Movies table, using movie_id

  movie_values = Movie.query.filter_by(
      id=movie_id).order_by('id').all()

  for movie in movie_values:
    json_past_comeouts = []
    json_upcoming_comeouts = []

  comeout_list = ComeOut.query.filter_by(movie_id=movie_id).order_by('id').all()
  var_upcoming_comeouts_count=0;
  var_past_comeouts_count = 0
  for comeout_lis in comeout_list:
    actor_list = Actor.query.filter_by(id=comeout_lis.actor_id).order_by('id').all()
    if (len(actor_list) > 0):
      if ((comeout_lis.start_time).strftime("%Y/%M/%D, %H:%M:%S") < (datetime.now()).strftime("%Y/%M/%D, %H:%M:%S")):
          for actor in actor_list:
            json_past_comeouts.append({"actor_id": comeout_lis.actor_id, "actor_name": actor.name,
                                    "actor_image_link": actor.image_link, "start_time": (comeout_lis.start_time).strftime("%m/%d/%Y, %H:%M:%S")})
          var_past_comeouts_count = len(json_past_comeouts)
      if ((comeout_lis.start_time).strftime("%Y/%M/%D, %H:%M:%S") > (datetime.now()).strftime("%Y/%M/%D, %H:%M:%S")):
          for actor in actor_list:
            json_upcoming_comeouts.append({"actor_id": comeout_lis.actor_id, "actor_name": actor.name,
                                    "actor_image_link": actor.image_link, "start_time": (comeout_lis.start_time).strftime("%m/%d/%Y, %H:%M:%S")})
          var_upcoming_comeouts_count = len(json_upcoming_comeouts)

  for movie in movie_values:
    data = {"id": movie.id, "name": movie.name,
             "genres": eval(movie.genres), "address":movie.address,
             "city": movie.city, "state": movie.state, "phone": movie.phone, "website": movie.website,
             "facebook_link": movie.facebook_link, "seeking_talent": movie.seeking_talent,
             "seeking_description": movie.seeking_description, "image_link": movie.image_link,
             "past_ComeOuts": json_past_comeouts,
             "upcoming_ComeOuts": json_upcoming_comeouts,
             "past_ComeOuts_count": var_past_comeouts_count, "upcoming_comeouts_count": var_upcoming_comeouts_count}

  #print(data)
  return render_template('pages/show_movie.html', movie=data)


#  Create Movie
#  ----------------------------------------------------------------

@app.route('/movies/create', methods=['GET'])
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth('get:movies')
def create_movie_form():
  form = MovieForm()
  return render_template('forms/new_movie.html', form=form)

@app.route('/movies/create', methods=['POST'])
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth('post:movies')
def create_movie_submission():
  # TODO: insert form data as a new Movie record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  address = request.form['address']
  city = request.form['city']
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  website = request.form['website']
  genres = request.form['genres']
  name = request.form['name']
  phone = request.form['phone']
  state = request.form['state']
  seeking_talent = request.form['seeking_talent']
  seeking_description = request.form['seeking_description']
  if(seeking_talent == "True"):
    seeking_talent = bool(seeking_talent)
  else:
    seeking_talent = bool()

  error = False
  try:
    movie = Movie(address=address, city=city, facebook_link=facebook_link,
                 genres="['"+genres+"']", name=name, phone=phone, state=state, 
                 past_comeouts_count=0,
                  upcoming_comeouts_count=0, seeking_talent=seeking_talent, 
                  past_comeouts="[]", upcoming_comeouts="[]",
                  image_link=image_link, website=website, 
                  seeking_description=seeking_description, title='hola', 
                  release_date='01/09/1988')
    movie.insert()
  except:
    error = True
  if error:
    flash('An error occurred. Movie could not be listed.')
  else:
    flash('Movie ' + request.form['name'] + ' was successfully listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Movie ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/movies/<movie_id>', methods=['DELETE'])
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth('delete:movies')
def delete_movie(movie_id):
  # TODO: Complete this endpoint for taking a movie_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    comeout = ComeOut.query.filter_by(movie_id=movie_id)
    movie = Movie.query.filter_by(id=movie_id)
    comeout.delete()
    movie.delete()
  except:
    error = True
  if error:
    flash('An error occurred. Movie could not be removed.')
    return redirect(url_for('index'))
  else:
    flash('Movie was successfully removed!')
    return redirect(url_for('index'))

  # BONUS CHALLENGE: Implement a button to delete a Movie on a Movie Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')


#  Actors
#  ----------------------------------------------------------------
@app.route('/actors')
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth('get:actors')
def actors():
  # TODO: replace with real data returned from querying the database

  data = []
  actor_list = Actor.query.with_entities(
      Actor.id, Actor.name).order_by('id').all()

  for Actor_lis in actor_list:
    data.append({"id": Actor_lis.id,
                  "name": Actor_lis.name})

  return render_template('pages/actors.html', actors=data)

@app.route('/actors/search', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth('post:actors')
def search_actors():
  # TODO: implement search on Actors with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  search = "%"+search_term+"%"
  actor_list = Actor.query.with_entities(Actor.id, Actor.name, Actor.upcoming_comeouts_count).filter(
      Actor.name.ilike(search)).order_by('id').all()
  count = Actor.query.with_entities(
      Actor.id, Actor.name, Actor.upcoming_comeouts_count).filter(Actor.name.ilike(search)).count()
  data = []
  for actor in actor_list:
    data.append({"id": actor.id, "name": actor.name,
                 "num_upcoming_comeouts": actor.upcoming_comeouts_count})
  response = {"count": count, "data": actor_list}

  return render_template('pages/search_actors.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/actors/<int:actor_id>')
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth('get:actors')
def show_actor(actor_id):
  # ComeOuts the Movie page with the given movie_id
  # TODO: replace with real Movie data from the Movies table, using movie_id

  actor_values = Actor.query.filter_by(
      id=actor_id).order_by('id').all()

  for actor in actor_values:
    json_past_comeouts = []
    json_upcoming_comeouts = []
    
  comeout_list = ComeOut.query.filter_by(actor_id=actor_id).order_by('id').all()
  var_upcoming_comeouts_count=0;
  var_past_comeouts_count = 0
  for comeout_lis in comeout_list:
    movie_list = Movie.query.filter_by(id=comeout_lis.movie_id).order_by('id').all()
    if (len(movie_list) > 0):
      if ((comeout_lis.start_time).strftime("%Y/%M/%D, %H:%M:%S") < (datetime.now()).strftime("%Y/%M/%D, %H:%M:%S")):
        for movie in movie_list:
          json_past_comeouts.append({"movie_id": comeout_lis.movie_id, "movie_name": comeout_lis.movie_name,
                                  "movie_image_link": movie.image_link, "start_time": (comeout_lis.start_time).strftime("%m/%d/%Y, %H:%M:%S")})
          var_past_comeouts_count = len(json_past_comeouts)
      if ((comeout_lis.start_time).strftime("%Y/%M/%D, %H:%M:%S") > (datetime.now()).strftime("%Y/%M/%D, %H:%M:%S")):
        for movie in movie_list:
          json_upcoming_comeouts.append({"movie_id": comeout_lis.movie_id, "movie_name": comeout_lis.movie_name,
                                  "movie_image_link": movie.image_link, "start_time": (comeout_lis.start_time).strftime("%m/%d/%Y, %H:%M:%S")})
          var_upcoming_comeouts_count = len(json_upcoming_comeouts)

  for actor in actor_values:
    data = {"id": actor.id, "name": actor.name,
            "genres": eval(actor.genres), 
            "city": actor.city, "state": actor.state, "phone": actor.phone, "age":actor.age,"website": actor.website,
            "facebook_link": actor.facebook_link, "seeking_movie": actor.seeking_movie,
            "seeking_description": actor.seeking_description, "image_link": actor.image_link,
            "past_ComeOuts": json_past_comeouts,
            "upcoming_ComeOuts": json_upcoming_comeouts,
            "past_ComeOuts_count": var_past_comeouts_count, "upcoming_comeouts_count": var_upcoming_comeouts_count}
            
  #data = list(filter(lambda d: d['id'] == actor_id, [data1, data2, data3]))[0]
  #data = data
  return render_template('pages/show_actor.html', actor=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/actors/<int:actor_id>/edit', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth('get:actors')
def edit_actor(actor_id):
  form = ActorForm()

  actor_values = Actor.query.filter_by(
      id=actor_id).order_by('id').all()

  for actor in actor_values:
    actorList = {"id": actor.id, "name": actor.name,
            "genres": eval(actor.genres),
            "city": actor.city, "state": actor.state, "phone": actor.phone, "age":actor.age,"website": actor.website,
            "facebook_link": actor.facebook_link, "seeking_movie": actor.seeking_movie,
            "seeking_description": actor.seeking_description, "image_link": actor.image_link
            }

  actorList=actorList
  # TODO: populate form with fields from Actor with ID <actor_id>
  return render_template('forms/edit_actor.html', form=form, actor=actorList)

@app.route('/actors/<int:actor_id>/edit', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth('post:actors')
def edit_actor_submission(actor_id):

  # TODO: take values from the form submitted, and update existing
  # Actor record with ID <actor_id> using the new attributes
  try:
    city = request.form.get('city', '')
    facebook_link = request.form.get('facebook_link', '')
    image_link = request.form.get('image_link', '')
    website = request.form.get('website', '')
    genres = request.form.get('genres', '')
    age = request.form.get('age', '')
    name = request.form.get('name', '')
    phone = request.form.get('phone', '')
    state = request.form.get('state', '')
    seeking_movie = request.form.get('seeking_movie', '')
    seeking_description = request.form.get('seeking_description', '')
    if(seeking_movie == "True"):
      seeking_movie = bool(seeking_movie)
    else:
      seeking_movie = bool()

    actor = Actor.query.get(actor_id)
    actor.city = city
    actor.facebook_link = facebook_link
    actor.image_link = image_link
    actor.genres = "['"+genres+"']"
    actor.name = name
    actor.phone = phone
    actor.age = age
    actor.state = state
    actor.website=website
    actor.seeking_movie = seeking_movie
    actor.seeking_description = seeking_description
    actor.insert()
  except:
    actor.rollback()
  finally:
    actor.close()
  return redirect(url_for('show_actor', actor_id=actor_id))

@app.route('/movies/<int:movie_id>/edit', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth('get:movies')
def edit_movie(movie_id):
  form = MovieForm()

  movie_values = Movie.query.filter_by(
      id=movie_id).order_by('id').all()

  for movies in movie_values:
    movie = {"id": movies.id, "name": movies.name,
             "genres": eval(movies.genres), "address": movies.address,
              "city": movies.city, "state": movies.state, "phone": movies.phone, "website": movies.website,
              "facebook_link": movies.facebook_link, "seeking_talent": movies.seeking_talent,
              "seeking_description": movies.seeking_description, "image_link": movies.image_link
              }

  # TODO: populate form with values from Movie with ID <movie_id>
  return render_template('forms/edit_movie.html', form=form, movie=movie)


@app.route('/movies/<int:movie_id>/edit', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth('post:movies')
def edit_movie_submission(movie_id):
  # TODO: take values from the form submitted, and update existing
  # Movie record with ID <movie_id> using the new attributes
  try:
    city = request.form.get('city', '')
    address = request.form.get('address', '')
    facebook_link = request.form.get('facebook_link', '')
    image_link = request.form.get('image_link', '')
    website = request.form.get('website', '')
    genres = request.form.get('genres', '')
    name = request.form.get('name', '')
    phone = request.form.get('phone', '')
    state = request.form.get('state', '')
    seeking_talent = request.form.get('seeking_talent', '')
    seeking_description = request.form.get('seeking_description', '')
    if(seeking_talent == "True"):
      seeking_talent = bool(seeking_talent)
    else:
      seeking_talent = bool()
    print('genres', genres)
    movie = Movie.query.get(movie_id)
    movie.city = city
    movie.facebook_link = facebook_link
    movie.image_link = image_link
    movie.genres = "['"+genres+"']"
    movie.name = name
    movie.phone = phone
    movie.state = state
    movie.address = address
    movie.website = website
    movie.seeking_talent = seeking_talent
    movie.seeking_description = seeking_description
    movie.insert()
  except:
    movie.rollback()
  finally:
    movie.close()
  return redirect(url_for('show_movie', movie_id=movie_id))

#  Create Actor
#  ----------------------------------------------------------------

@app.route('/actors/create', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth('get:actors')
def create_actor_form():
  form = ActorForm()
  print(form)
  return render_template('forms/new_actor.html', form=form)

@app.route('/actors/create', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth('post:actors')
def create_actor_submission():
  # called upon submitting the new Actor listing form
  # TODO: insert form data as a new Movie record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  city = request.form['city']
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  website = request.form['website']
  genres = request.form['genres']
  name = request.form['name']
  phone = request.form['phone']
  age = request.form['age']
  state = request.form['state']
  seeking_movie = request.form['seeking_movie']
  seeking_description = request.form['seeking_description']
  if(seeking_movie=="True"):
    seeking_movie = bool(seeking_movie)
  else:
    seeking_movie = bool()
  error = False
  try:
    actor = Actor(city=city, facebook_link=facebook_link, image_link=image_link,
                  genres="['"+genres+"']", name=name, phone=phone, state=state, past_comeouts_count=0,
                  upcoming_comeouts_count=0, past_comeouts="[]", upcoming_comeouts="[]", 
                    website=website, seeking_movie=seeking_movie, seeking_description=seeking_description,
                    gender="['"+genres+"']",age=age)
    actor.insert()
  except:
    error = True
  if error:
    flash('An error occurred. Actor could not be listed.')
  else:
    flash('Actor ' + request.form['name'] + ' was successfully listed!')

  # on successful db insert, flash success
  #flash('Actor ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Actor ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  ComeOuts
#  ----------------------------------------------------------------



@app.route('/comeouts')
#@cross_origin(headers)
#@requires_auth('get:comeouts')
def comeouts():
  # displays list of ComeOuts at /ComeOuts
  # TODO: replace with real Movies data.
  #       num_ComeOuts should be aggregated based on number of upcoming ComeOuts per Movie.
  
  data = []

  comeout_list = ComeOut.query.order_by('id').all()

  for comeout_lis in comeout_list:
    data.append({"movie_id": comeout_lis.movie_id,
                 "movie_name": comeout_lis.movie_name,
                 "actor_id": comeout_lis.actor_id,
                 "actor_name": comeout_lis.actor_name,
                 "actor_image_link": comeout_lis.actor_image_link,
                 "start_time": (comeout_lis.start_time).strftime("%m/%d/%Y, %H:%M:%S")})
  return render_template('pages/comeouts.html', comeouts=data)

@app.route('/comeouts/create')
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth('get:comeouts')
def create_comeouts():
  # renders form. do not touch.
  form = ComeOutForm()
  return render_template('forms/new_comeout.html', form=form)

@app.route('/comeouts/create', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth('post:comeouts')
def create_comeout_submission():
  # called to create new ComeOuts in the db, upon submitting new ComeOut listing form
  # TODO: insert form data as a new ComeOut record in the db, instead

  actor_id = request.form['actor_id']
  start_time = request.form['start_time']
  movie_id = request.form['movie_id']

  actor_values = Actor.query.filter_by(
      id=actor_id).order_by('id').all()

  movie_values = Movie.query.filter_by(
      id=movie_id).order_by('id').all()

  var_movie_name=""
  
  for movie in movie_values:
    var_movie_name = movie.name

  var_actor_name = ""
  var_actor_image_link = ""
  
  for actor in actor_values:
    var_actor_name = actor.name
    var_actor_image_link = actor.image_link

  error = False
  try:
    print(format_datetime(start_time.strip(),""))
    comeout = ComeOut(actor_id=actor_id, start_time=start_time.strip(),
                movie_id=movie_id, actor_name=var_actor_name,
                actor_image_link=var_actor_image_link, movie_name=var_movie_name)
    comeout.insert()
  except:
    error = True
  if error:
    flash('An error occurred. Actor ID and Movie ID could not be listed.')
  else:
    flash('Actor ID ' + request.form['actor_id'] + ' and Movie ID ' +
          request.form['movie_id'] + ' was successfully listed!')

  # on successful db insert, flash success
  #flash('ComeOut was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. ComeOut could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


'''@app.route('/comeouts/create')
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth('get:comeouts')
def create_comeouts():
  # renders form. do not touch.
  form = ComeOutForm()
  return render_template('forms/new_comeout.html', form=form)

@app.route('/comeouts/create', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
#@requires_auth('post:comeouts')
def create_comeout_submission():
  # called to create new comeouts in the db, upon submitting new comeout listing form
  # TODO: insert form data as a new ComeOut record in the db, instead

  actor_id = request.form['actor_id']
  start_time = request.form['start_time']
  movie_id = request.form['movie_id']

  actor_values = Actors.query.filter_by(
      id=actor_id).order_by('id').all()

  movie_values = Movies.query.filter_by(
      id=movie_id).order_by('id').all()

  var_movie_title=""
  
  for movie in movie_values:
    var_movie_title = movie.title

  var_actor_name = ""
  var_actor_image_link = ""
  
  for actor in actor_values:
    var_actor_name = actor.name
    var_actor_image_link = actor.image_link

  error = False
  try:
    print(format_datetime(start_time.strip(),""))
    comeout = ComeOut(actor_id=actor_id, start_time=start_time.strip(),
                movie_id=movie_id, actor_name=var_actor_name,
                actor_image_link=var_actor_image_link, movie_title=var_movie_title)
    comeout.insert()
  except:
    error = True
    comeout.rollback()
    print(sys.exc_info())
  finally:
    comeout.close()
  if error:
    flash('An error occurred. Actor ID ' + actor_id +
          ' and Movie ID ' + movie_id + ' could not be listed.')
  else:
    flash('ACtor ID ' + request.form['actor_id'] + ' and Movie ID ' +
          request.form['movie_id'] + ' was successfully listed!')

  # on successful db insert, flash success
  #flash('ComeOut was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. ComeOut could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')
'''


# /server.py
# Here we're using the /callback route.
@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    print(userinfo)

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/dashboard')

# /server.py
@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri='https://castingagencyfsnd1.herokuapp.com/', audience=os.environ['API_AUDIENCE'])

# /server.py
@app.route('/dashboard')
def dashboard():
    return render_template('pages/home.html',
                           userinfo=session['profile'],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))

# /server.py
@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('index', _external=True), 'client_id': 'fEDJSnB6Gb57nXJWzdTakt1x1N39x6EU'}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))




@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    print(response)
    return render_template('errors/401.html'), 401





@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(401)
def not_found_error(error):
    return render_template('errors/401.html'), 401

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return render_template('errors/422.html'), 422


@app.errorhandler(405)
def method_not_allowed(error):
    return render_template('errors/405.html'), 405


@app.errorhandler(503)
def bad_request(error):
    return render_template('errors/503.html'), 503

@app.errorhandler(403)
def user_error(error):
    return render_template('errors/403.html'), 403

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, debug=True)

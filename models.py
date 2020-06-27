import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

'''database_name = "agency"
database_path = "postgres://{}/{}".format(
    'agency:agency@localhost:5432', database_name)'''

SECRET_KEY = os.urandom(32)

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SECRET_KEY'] = SECRET_KEY
    db.app = app
    db.init_app(app)
    db.create_all()

'''
movies
'''
class Movie(db.Model):
    __tablename__ = 'movie'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(500))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(2000))
    past_comeouts = db.Column(db.String())
    upcoming_comeouts = db.Column(db.String())
    past_comeouts_count = db.Column(db.Integer, nullable=False, default=0)
    upcoming_comeouts_count = db.Column(db.Integer, nullable=False, default=0)
    title = Column(String)
    release_date = Column(String)
    #comeout = db.relationship('comeout', backref='list', cascade='all, delete-orphan')


    def __init__(self, name, genres, city, state, address, phone, title, website, 
    facebook_link, seeking_talent, seeking_description, image_link, past_comeouts,
    upcoming_comeouts, past_comeouts_count, upcoming_comeouts_count, release_date):
      self.name = name
      self.title = title
      self.release_date = release_date
      self.genres = genres
      self.city= city
      self.state = state
      self.address = address
      self.phone =phone
      self.website = website
      self.facebook_link = facebook_link
      self.seeking_talent = seeking_talent
      self.seeking_description = seeking_description
      self.image_link = image_link
      self.past_comeouts = past_comeouts
      self.upcoming_comeouts = upcoming_comeouts
      self.past_comeouts_count = past_comeouts_count
      self.upcoming_comeouts_count = upcoming_comeouts_count
      self.release_date = release_date

    def insert(self):
      db.session.add(self)
      db.session.commit()

    def update(self):
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()

    def close(self):
      db.session.close()

    def rollback(self):
      db.session.rollback()

    def format(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'address': self.address,
        'phone': self.phone,
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'seeking_talent': self.seeking_talent,
        'seeking_description': self.seeking_description,
        'image_link': self.image_link,
        'past_comeouts': self.past_comeouts,
        'upcoming_comeouts': self.upcoming_comeouts,
        'past_comeouts_count': self.past_comeouts_count,
        'upcoming_comeouts_count': self.upcoming_comeouts_count,
        'genres': self.genres,
        'title': self.title,
        'release_date': self.release_date
      }


class Actor(db.Model):
    __tablename__ = 'actor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(500))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_movie = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(3000))
    past_comeouts = db.Column(db.String())
    upcoming_comeouts = db.Column(db.String())
    past_comeouts_count = db.Column(db.Integer, nullable=False, default=0)
    upcoming_comeouts_count = db.Column(db.Integer, nullable=False, default=0)
    gender = db.Column(db.String(500))
    age = db.Column(db.String(120))

    def __init__(self, name, age, genres, city, state, phone, website, facebook_link,
    seeking_movie, seeking_description, image_link, past_comeouts, upcoming_comeouts, 
    past_comeouts_count, upcoming_comeouts_count, gender):
      self.name = name
      self.age = age
      self.genres = genres
      self.city = city
      self.state = state
      self.phone = phone
      self.website = website
      self.facebook_link = facebook_link
      self.seeking_movie = seeking_movie
      self.seeking_description = seeking_description
      self.image_link = image_link
      self.past_comeouts = past_comeouts
      self.upcoming_comeouts = upcoming_comeouts
      self.past_comeouts_count = past_comeouts_count
      self.upcoming_comeouts_count = upcoming_comeouts_count
      self.gender = gender

    def insert(self):
      db.session.add(self)
      db.session.commit()
    
    def update(self):
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()

    def close(self):
      db.session.close()

    def rollback(self):
      db.session.rollback()

    def format(self):
      return {
        'id': self.id,
        'name': self.name,
        'genres': self.genres,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'website': self.website,
        'facebook_link': self.facebook_link,
        'seeking_movie': self.seeking_movie,
        'seeking_description': self.seeking_description,
        'image_link': self.image_link,
        'past_comeouts': self.past_comeouts,
        'upcoming_comeouts': self.upcoming_comeouts,
        'past_comeouts_count': self.past_comeouts_count,
        'upcoming_comeouts_count': self.upcoming_comeouts_count,
        'age': self.age,
        'gender': self.gender
      }


class ComeOut(db.Model):
    __tablename__ = 'comeout'

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey(
        'movie.id'), nullable=False)
    movie_name = db.Column(db.String)
    actor_id = db.Column(db.Integer, db.ForeignKey(
        'actor.id'), nullable=False)
    actor_name = db.Column(db.String)
    actor_image_link = db.Column(db.String(500))
    start_time = db.Column(db.DateTime(timezone=True))

    def __init__(self, movie_id, movie_name, actor_id, actor_name, actor_image_link, start_time):
      self.movie_id = movie_id
      self.movie_name = movie_name
      self.actor_id = actor_id
      self.actor_name = actor_name
      self.actor_image_link = actor_image_link
      self.start_time = start_time

    def insert(self):
      db.session.add(self)
      db.session.commit()
    
    def update(self):
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()

    def close(self):
      db.session.close()

    def rollback(self):
      db.session.rollback()

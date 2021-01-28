import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movies, Actor
from auth.auth import AuthError, requires_auth
from datetime import datetime

ROWS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    # CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    def paginate_results(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * ROWS_PER_PAGE
        end = start + ROWS_PER_PAGE
        objects_formatted = [object_name.format() for object_name in selection]
        return objects_formatted[start:end]

    @app.route('/')
    def hello():
        return "Welcome to capstone project"

    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def get_actors(token):
        selection = Actor.query.all()
        actors_paginated = paginate_results(request, selection)
        if len(actors_paginated) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'actors': actors_paginated
            })

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def insert_actors(token):
        body = request.get_json()
        name = body.get('name', None)
        age = body.get('age', None)
        gender = body.get('gender', None)
        m_id = body.get('movie_id', None)
        if not name:
            abort(422, {'message': 'no name provided.'})

        if not age:
            abort(422, {'message': 'no age provided.'})

        try:
            new_actor = Actor(name=name, age=age, gender=gender, movie_id=m_id)
            new_actor.insert()
            return jsonify({
                'success': True,
                'message': new_actor.id
                })
        except:
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('edit:actors')
    def edit_actors(token, actor_id):
        body = request.get_json()
        name = body.get('name', None)
        age = body.get('age', None)
        gender = body.get('gender', None)
        # try:
        actor = Actor.query.filter_by(id=actor_id).one_or_none()
        if actor is None:
            abort(404)
        if name is not None:
            actor.name = name
        if age is not None:
            actor.age = age
        if gender is not None:
            actor.gender = gender
        actor.update()
        return jsonify({
            'success': True,
            'updated': actor.id,
            'actor': [actor.format()]
            })
        # except:
        # abort(422)

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actors(token, actor_id):
        try:
            actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
            if actor is None:
                abort(404)
            actor.delete()
            return jsonify({
                'success': True,
                'deleted': actor_id
                })
        except:
            abort(422)

    @app.route('/movies', methods=['GET'])
    @requires_auth('get:movies')
    def get_movies(token):
        selection = Movies.query.all()
        movies_paginated = paginate_results(request, selection)
        if len(movies_paginated) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'movies': movies_paginated
            })

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def insert_movies(token):
        body = request.get_json()
        title = body.get('title', None)
        release_date = body.get('release_date', None)
        if not title:
            abort(422, {'message': 'no title provided.'})
        if not release_date:
            abort(422, {'message': 'no "release_date" provided.'})

        try:
            new_movie = Movies(title=title, release_date=release_date)
            new_movie.insert()
            return jsonify({
                'success': True,
                'message': new_movie.id
                })
        except:
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('edit:movies')
    def edit_movies(token, movie_id):
        body = request.get_json()
        title = body.get('title', None)
        release_date = body.get('release_date', None)
        # try:
        movie = Movies.query.filter_by(id=movie_id).one_or_none()
        if movie is None:
            abort(404)
        if title is not None:
            movie.title = title
        if release_date is not None:
            movie.release_date = release_date
        movie.update()
        return jsonify({
            'success': True,
            'updated': movie.id,
            'actor': [movie.format()]
            })
        # except:
        # abort(422)

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movies(token, movie_id):
        try:
            movie = Movies.query.filter(Movies.id == movie_id).one_or_none()
            if movie is None:
                abort(404)
            movie.delete()
            return jsonify({
                'success': True,
                'deleted': movie_id
                })
        except:
            abort(422)

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
            }), 422

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
            }), 404

    @app.errorhandler(AuthError)
    def auth_error(e):
        return jsonify({
            "message": e.error,
            "code": e.status_code}), e.status_code
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    
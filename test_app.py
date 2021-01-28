import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import setup_db, Movies, Actor
from config import bearer_tokens
from sqlalchemy import desc
from datetime import date

casting_assistant_auth_header = {
    'Authorization': bearer_tokens['casting_assistant']
}

casting_director_auth_header = {
    'Authorization': bearer_tokens['casting_director']
}

executive_producer_auth_header = {
    'Authorization': bearer_tokens['executive_producer']
}


class CapstoneTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "capstone_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
                                                             'postgres',
                                                             '6541',
                                                             'localhost:5432',
                                                             self.database_name
                                                             )
        setup_db(self.app, self.database_path)
        self.type = None
        self.json_create_actor = Actor("Ahmed", "22",
                                       "male", self.type).format()
        self.json_edit_actor_with_new_age = Actor("Ahmed", "29",
                                                  "male", self.type).format()
        self.json_create_movie = Movies("oil", "2015-08-07 05:00:01").format()
        self.json_edit_movie = Movies("oil", "2020-08-09 05:00:01").format()
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_create_new_actor(self):
        res = self.client().post('/actors', json=self.json_create_actor,
                                 headers={'Authorization':
                                          bearer_tokens['executive_producer']})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_error_401_new_actor(self):
        res = self.client().post('/actors', json=self.json_create_actor)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertTrue(data['message'])

    def test_get_all_actors(self):
        res = self.client().get('/actors?page=1', headers={
            'Authorization': bearer_tokens['casting_assistant']})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['actors']) > 0)

    def test_error_401_get_all_actors(self):
        res = self.client().get('/actors?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertTrue(data['message'])

    def test_edit_actor(self):
        res = self.client().patch('/actors/33',
                                  json=self.json_edit_actor_with_new_age,
                                  headers={'Authorization':
                                           bearer_tokens['casting_director']})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_error_404_edit_actor(self):
        res = self.client().patch('/actors/123412',
                                  json=self.json_edit_actor_with_new_age,
                                  headers={'Authorization':
                                           bearer_tokens['casting_director']})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_error_401_delete_actor(self):
        res = self.client().delete('/actors/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertTrue(data['message'])

    def test_delete_actor(self):
        res = self.client().delete('/actors/35', headers={
            'Authorization': bearer_tokens['casting_director']})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], 35)

    def test_create_new_movie(self):
        res = self.client().post('/movies', json=self.json_create_movie,
                                 headers={'Authorization':
                                          bearer_tokens['executive_producer']})
        data = json.loads(res.data)
        print(data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_error_401_new_movie(self):
        res = self.client().post('/movies', json=self.json_create_movie)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertTrue(data['message'])

    def test_get_all_movies(self):
        res = self.client().get('/movies?page=1',
                                headers={'Authorization':
                                         bearer_tokens['casting_director']})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['movies']) > 0)

    def test_error_401_get_all_movies(self):
        res = self.client().get('/movies?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertTrue(data['message'])

    def test_edit_movie(self):
        res = self.client().patch('/movies/5', json=self.json_edit_movie,
                                  headers={'Authorization':
                                           bearer_tokens['executive_producer']
                                           })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_error_404_edit_movie(self):
        res = self.client().patch('/movies/1779', json=self.json_edit_movie,
                                  headers={'Authorization':
                                           bearer_tokens['casting_director']})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_error_401_delete_movie(self):
        res = self.client().delete('/movies/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertTrue(data['message'])

    def test_delete_movie(self):
        res = self.client().delete('/movies/6', headers={
            'Authorization': bearer_tokens['executive_producer']})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], 6)


if __name__ == "__main__":
    unittest.main()

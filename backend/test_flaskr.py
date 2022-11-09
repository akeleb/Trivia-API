import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

import sys
import traceback

try:
    assert True
    assert 7 == 7
    assert 1 == 2
    # many more statements like this
except AssertionError:
    _, _, tb = sys.exc_info()
    traceback.print_tb(tb) # Fixed format
    tb_info = traceback.extract_tb(tb)
    filename, line, func, text = tb_info[-1]

    print('An error occurred on line {} in statement {}'.format(line, text))
    exit(1)
    


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql+psycopg2://postgres:Aklexsqldb14@localhost:5432/udacityexc".format('localhost:5432',self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_request_beyond_valid_page(self):
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_delete_question(self):

        question = Question(question='test_question',
                            answer='test_answer',
                            category='2',
                            difficulty=4)
        question.insert()
        response = self.client().delete(f'/questions/{question.id}')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question.id)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        question = Question.query.filter(Question.id == question.id).one_or_none()
        self.assertEqual(question, None)

    def test_create_new_question(self):
        response = self.client().post('/questions', json={'question':'test_question',
                                                         'answer': 'test_answer',
                                                         'difficulty': 3,
                                                         'category': '3'})
        data = json.loads(response.data)
        question = Question.query.filter_by(id=data['created']).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(question)
        question.delete()

    def test_422_if_question_creation_fails(self):
        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_search_questions(self):
        response = self.client().post('/search',json={'searchTerm': 'Taj Mahal'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_404_if_search_questions_fails(self):
        response = self.client().post('/search',json={'searchTerm': 'vlcmdssvdv'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_for_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['current_category'], 'Science')

    def test_400_if_questions_by_category_fails(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_play_quiz_game(self):
        response = self.client().post('/quizes',
                                      json={'previous_questions': [10],
                                            'quiz_category': {'type': 'Science', 'id': '1'}})

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        # check that the returned qestion is in the right category
        self.assertEqual(data['question']['category'], 1)
        self.assertNotEqual(data['question']['id'], 10)

    def test_play_quiz_fails(self):
        response = self.client().post('/quizes', json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
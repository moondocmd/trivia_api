import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','pass', 'localhost:5432', self.database_name)

        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Hello question world?',
            'answer': 'Test completing!',
            'difficulty': 5,
            'category': 3
        }

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
        res = self.client().get('/questions')
        data = json.loads(res.data)
        print ("running questions test")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
    
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000', json={'difficulty': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        print ("running categories test")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_get_specific_category_questions(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        print ("running specific category test")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))

    # # @TODO: Write tests for search - at minimum two
    # #        that check a response when there are results and when there are none

    def test_question_search_positive(self):
        self.search_term={'searchTerm':'title'} #test a positive case
        res = self.client().post('/questions/search', json= self.search_term)
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

    def test_question_search_negative(self): 
        self.search_term={'searchTerm': None} #test a negative case
        res = self.client().post('/questions/search', json= self.search_term)
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_question_search_noresults(self): 
        self.search_term={'searchTerm': "ZZZZZZZZZZZZZ"} #test returning no results (empty list)
        res = self.client().post('/questions/search', json= self.search_term)
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200) #200 since the server did not experience any errors, simply returned an empty result list
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0) # confirm no questions were returned

    def test_quiz_play(self):   
        res = self.client().post('/quizzes', json= {"quiz_category" : 1, "previous_questions": []}) #test a quiz 
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_delete_question(self):
        res = self.client().delete('/questions/4')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 4).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 4)
        self.assertEqual(question, None)
        

    def test_404_if_questions_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
    
    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        pass
    
    def test_422_if_question_creation_fails(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        pass

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
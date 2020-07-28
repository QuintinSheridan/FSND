import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

user = os.environ['USERNAME']
pword = os.environ['PW']

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = f'postgres://{user}:{pword}@localhost:5432/{self.database_name}'
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'What is the tallest capital city?',
            'answer': 'La Paz',
            'difficulty': 4,
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

    # """
    # TODO
    # Write at least one test for each test for successful operation and for expected errors.
    # """

    def test_get_categories(self):
        # success
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])


    def test_get_questions(self):
        # success
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])


    def test_create_question(self):
        # success
        response = self.client().post('/questions', json = self.new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertTrue(data['answer'])
        self.assertTrue(data['difficulty'])
        self.assertTrue(data['category'])
        self.assertTrue(data['created'])

        delete_id = data['created']

        # 405
        response405 = self.client().post('/questions/1', json = self.new_question)
        data405 = json.loads(response.data)

        self.assertEqual(response405.status_code, 405)

    
    def test_delete_question(self):
        # success
        create_response = self.client().post('/questions/add', json = self.new_question)
        create_data = json.loads(create_response.data)
        delete_id = create_data['created']

        print(f"delete_id : {delete_id}")
        response = self.client().delete(f'/questions/{delete_id}')
        data = json.loads(response.data)
        question = Question.query.filter(Question.id == delete_id).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], delete_id)
        self.assertTrue(data['categories'])
        self.assertEqual(question, None)

        # 404 qeustion not found
        response404 = self.client().delete('/questions/1000')
        data404 = json.loads(response404.data)

        #self.assertEqual(response404.status_code, 200)
        self.assertEqual(data404['error'], 404)
        self.assertEqual(data404['success'], False)
        self.assertEqual(data404['message'], 'resource not found')

        # 405
        response405 = self.client().delete('/questions')
        data405 = json.loads(response.data)

        self.assertEqual(response405.status_code, 405)
     

    def test_search_question(self):
        # success for found questions
        response = self.client().post('/questions/search', json={'searchTerm':'what'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

        # sucess no matches
        response = self.client().post('/questions/search', json={'searchTerm':'zzzzzzzzzzzz'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse(data['questions'])
        self.assertEqual(data['total_questions'], 0)


    def test_get_category_questions(self):
        # success
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])


    def get_quiz_question(self):
        # success
        response = self.client().post('/quizzes', 
            json = {'previous_questions':[], 'quiz_category':1})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
    



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
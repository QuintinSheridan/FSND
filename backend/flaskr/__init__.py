import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page-1)*QUESTIONS_PER_PAGE
  end = start+QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response


  @app.route('/categories', methods=['GET'])
  def get_categories():
    # print('getting categories')
    cat_list = Category.query.order_by(Category.id).all()

    # 404 abort if unable to retrieve categories
    if len(cat_list) == 0:
      abort(404)

    categories = {}
    for cat in cat_list:
      categories[cat.id] = cat.type

    # print('Categories: ', categories)
    response = jsonify({
      'success': True,
      'categories': categories
    })
    # print('Category response: ', response)
    
    return response


  @app.route('/questions', methods=['GET'])
  def get_questions():
    print('WTF where are the questions?')
    questions = Question.query.order_by(Question.id).all()
    # if(questions):
    #   print(f'\n\n\n\n Successfully retrieved questions \n {questions} \n\n\n')
    #   for question in questions:
    #     print('formatted question : ', question.format())
    total_questions = len(questions)
    current_questions = paginate_questions(request, questions)

    if len(current_questions)==0:
      abort(404)

    cat_list = Category.query.order_by(Category.id).all()
    # print('cat_list: ', cat_list)
    categories = {}
    for cat in cat_list:
      categories[cat.id] = cat.type
      # print('categories: ', categories)
    
    response = jsonify({
      'questions':current_questions,
      'total_questions':total_questions,
      'success':True,
      'categories':categories,
      'current_category':None
    })
    # print('getQuestions response: ', response)

    return response


  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    question = Question.query.filter(Question.id == id).one_or_none()
    # print('question: ', question)
    if question == None:
      # print('Question not found')
      abort(404)
    try:
      # print(f'Deleting Question {id}')
      question.delete()
      # print(f'Question {id} deleted')
      questions = Question.query.order_by(Question.id).all()
      # if(questions):
      #   print(f'\n\n\n\n Delete Successfully retrieved questions \n {questions} \n\n\n')
      total_questions = len(questions)
      current_questions = paginate_questions(request, questions)
      categories = [c.format() for c in Category.query.all()]

      response = jsonify({
          'questions':current_questions,
          'total_questions':total_questions,
          'success':True,
          'categories':categories,
          'current_category':None,
          'deleted':id
        })

      return response

    except:
      abort(422)


  @app.route('/questions', methods=['POST'])
  def create_question():
    try:
      body = request.get_json()
      # print(f'\n\n\n body: {body} \n\n\n')
      question = body.get('question', None)
      answer = body.get('answer', None)
      difficulty = body.get('difficulty', None)
      category = body.get('category', None)
      
      q=Question(question=question, answer=answer, 
        difficulty=difficulty, category=category)
      q.insert()
      # print('Created Question: ', q.format())
      
      return jsonify({
        'question': question,
        'answer': answer,
        'difficulty': difficulty,
        'category': category,
        'success':  True,
        'created': q.id
      })
    
    except:
      abort(422)


  @app.route('/questions/search',methods=['POST'])
  def search_question():
    data = request.args
    print('data: ', data)
    # print('body: ', body)
    search_term = data['searchTerm']
    questions = Question.query.all()
    matching_questions = []

    if not questions:
      abort(404)

    for question in questions:
      if(search_term in question.question.lower()):
        matching_questions.append(question)

    current_questions = paginate_questions(request, matching_questions)
    total_questions = len(matching_questions)
    current_category = None

    return jsonify({
      'questions': current_questions, 
      'total_questions': total_questions,
      'current_category': current_category,
      'success': True
    })


  @app.route('/categories/<int:id>/questions',methods=['GET'])
  def get_category_questions(id):
    questions = Question.query.filter(Question.category == id).all()
    current_questions = paginate_questions(request, questions)
    total_questions = len(current_questions)
    current_category = id

    return jsonify({
      'questions': current_questions, 
      'total_questions': total_questions,
      'current_category': current_category,
      'success': True
    })


  @app.route('/quizzes',methods=['POST'])
  def get_quiz_question():
    body = request.args

    if 'quiz_category' not in body:
      abort(400)
    
    else:
      quiz_category = body['quiz_category']

    #print('body: ', body)
    if 'previous_questions' in body:
      previous_questions = body['previous_questions']
      quiz_category = body['quiz_category']
      question = Question.query.filter(Question.category == 
        quiz_category['id']).filter(Question.id.notin_(previous_questions)).first()
    #print(f'Quiz question')
    else:
      question = Question.query.filter(Question.category == 
        quiz_category['id']).first()

    return jsonify({
      'question': question.format(),
      'success': True
    })
  

##############################
# error handling
##############################
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': "resource not found"
    }), 404

  @app.errorhandler(422)
  def unable_to_process(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': "unable to process request"
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': "bad request"
    }), 400

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': "method not allowed"
    }), 405

  return app






    
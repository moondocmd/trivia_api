import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  #CORS(app)
  CORS(app, resources={r'*': {"origins": "*"}})

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  '''
  @TODO:   
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_categories():
    print("RETRIEVING CATEGORIES!!!!")
    categories = Category.query.order_by(Category.type).all()

    if len(categories) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'categories': {category.id: category.type for category in categories}
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''


  @app.route('/questions', methods=['GET'])
  def retrieve_questions():
    print("IM IN THE RETRIEVE Q's")
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    categories = Category.query.order_by(Category.type).all()

    if len(current_questions) == 0:
      abort(404)
    #print("WE got what we need! " + str(len(selection)) + " "+ str(current_questions))
    return jsonify({  #Do i need to return status code?
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection),
      'categories': {category.id: category.type for category in categories},
      'current_category': None
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    print("IM TRYING TO DELETE: " + str(question_id))
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      print("FUOND Q : " + str(question))
      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'success': True,
        'status': 200,
        'deleted': question_id
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    print("INSERTING")
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    try:
      question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      question.insert()
      print("INSERTED!")
      return jsonify({
        'success': True,
        'question': question.question
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  #@app.route('/questions/search', methods=['OPTIONS','POST'])
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
      # if not request.method == 'POST':
      #     abort(405)
      data = request.get_json()
      search_term = data.get('searchTerm', None)
      print("SEARCHING FOR: "+ str(search_term))
      if not search_term:
          abort(404)
      try:
          questions = Question.query.filter(
              Question.question.ilike('%{}%'.format(search_term))).all()

          #paginated_questions = paginate_questions(request, questions)
          return jsonify({
              'success': True,
              'status': 200,
              'questions': paginate_questions(request, questions),
              'total_questions': len(questions)
          })
      except:
          abort(404)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions(category_id):
    print("LOOKING FOR " + str(category_id))

    try:
      questions = Question.query.filter(Question.category == str(category_id)).all()
      if questions is None:
        abort(404)
      #current_questions = paginate_questions(request, questions)  CHANGED THIS, REVERT IF NEEDED
      #print(current_questions)
      return jsonify({
        'success': True,
        'current_category': category_id,
        'questions': paginate_questions(request, questions),
        'total_questions': len(questions)
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def send_quiz_data():
    print("LETS QUIZ!")
    data = request.get_json()
    category = data.get('quiz_category', None)
    previous_questions = data.get('previous_questions', None) 

    print("searched for " + str(category))
    print("previous q's : " + str(previous_questions))
    try:
      #questions = Question.query.filter(Question.category == str(category)).all()
      if category != 0:
        questions = Question.query.filter(Question.category == str(category)).filter(Question.id.notin_((previous_questions))).all()
      else:
        questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
      #print("HERE ARE THE Q's: " + str(questions))
      if questions is None:
        abort(404)
        
      current_questions = paginate_questions(request, questions)
      random_q = random.choice(current_questions)
      print("WEVE GOT A RANDOM Q " + str(random_q))
      return jsonify({
        'success': True,
        'current_category': category, #is this needed?
        'question': random_q,
      })
    except:
      print("NO QUESTION AVAILABLE! - ABORTING")
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

  return app

    
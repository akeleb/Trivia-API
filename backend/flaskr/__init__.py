
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from collections.abc import Mapping
import random
from models import setup_db, Question, Category,db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def add_access_control(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'ContentType,Authorization, True')

        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,POST,PUT,DELETE,UPDATE,OPTIONS')

        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """      
    @app.route('/categories', methods=['GET'])
    def get_categories():
        
        categoryDictionary ={}
        category = db.session.query(Category).order_by(Category.type).all()
        
        if len( category) == 0:
             abort(404)
            
        for items in category:
            categoryDictionary[items.id] = items.type     
              
        return jsonify({
            'success': True,
            'categories': categoryDictionary
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        all_questions = Question.query.order_by(Question.id).all()
        
        """
        Setting start / end points based on static
        QUESTIONS_PER_PAGE variable
        """
        """
         Applying pagination to incoming question set
        """
        current_questions = paginate_questions(request, all_questions)

        categories = Category.query.order_by(Category.type).all()

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(all_questions),
            'categories': {category.id: category.type
                           for category in categories},
            'current_category': None
        })


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except BaseException:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question
    """
    @app.route('/questions', methods=['POST'])
    def create_question():

        body = request.get_json()
        question = body.get('question')
        answer = body.get('answer')
        difficulty = body.get('difficulty')
        category = body.get('category')

        if not (question and answer and difficulty and category):
            abort(422)

        try:
            new_question = Question(question=question,
                                    answer=answer,
                                    difficulty=difficulty,
                                    category=category)

            new_question.insert()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': new_question.id,
                "question_created": question.question,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
            })

        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term
    """
    app.route('/search', methods=['POST'])
    def search_questions():
     try:
         body = request.get_json()
         search =  body.get('search_Item', None )
         if None not in (search):    
          results = Question.query.filter(Question.question.like('%' + search + '%')).all()
         questions= [question.format() for question in results]

         if search == None: 
            abort(404)

         return jsonify({
                "success": True,
                'question': list(questions),
                "all_questions": len( results),
            })
     except:
        abort(422)


    """
    @TODO:
    Create a GET endpoint to get questions based on category
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_questions(category_id):
        questions = Question.query.filter(
            Question.category == category_id).all()

        if len(questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': [question.format() for question in questions],
            'total_questions': len(questions),
            'current_category': category_id
        })
    

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz
    """
    @app.route('/quizes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()   
            quiz_category= body.get('quiz_category')
            previous_questions = body.get('previous_questions')
            category_id = quiz_category['id']
            if (quiz_category is None) or (previous_questions is None):
                abort(422) 

            if category_id == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(
                    Question.category == category_id).all()
            question = None
            if(questions):
                question = questions[random.randrange(0, len(questions), 1)]

            return jsonify({
                'success': True,
                'question': question.format()
            })
        except:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
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


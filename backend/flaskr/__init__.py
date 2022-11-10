
from logging import exception
import os
from shutil import ExecError
from unicodedata import category
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
            
        for items in category:
            categoryDictionary[items.id] = items.type
            
            if len(categoryDictionary)==0:
                abort(404)   
              
        return jsonify({
            'success': True,
            'categories': categoryDictionary,
            "total_categories":len(categoryDictionary)
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        all_questions = Question.query.order_by(Question.id).all()
        """
         Applying pagination to incoming question set
        """
        current_questions = paginate_questions(request, all_questions)
        categories = Category.query.order_by(Category.type).all()
        categoryDictionary = {}
        for item in categories:
            categoryDictionary[item.id] = item.type

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(all_questions),
            'categories': categoryDictionary,
        })


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
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
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        if (
                (new_question is None)
                or (new_answer is None)
                or (new_difficulty is None)
                or (new_category is None)
            ):
            abort(422)
        try:
            new_question = Question(question=new_question,
                                    answer=new_answer,
                                    difficulty=new_difficulty,
                                    category=new_category)

            new_question.insert()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': new_question.id,
                "question_created": new_question.question,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
            })

        except Exception as err:
            print(err)
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term
    """
    @app.route('/search', methods=['POST'])
    def search_questions():
        try:
            body = request.get_json()
            
            search = None
            if body.get("search_Item"):
                search = body.get('search_Item')
                
            results = Question.query.filter(Question.question.ilike(f"%{search}%")).all()
            
            current_questions = None
            if results:
                current_questions=  paginate_questions(request, results)
            
            if search == None or current_questions == None:
                abort(404)
                
            return jsonify({
                "success": True,
                'questions': current_questions,
                "total_questions": len(results),
                "current_category": current_questions[0]["category"]
            })
        except Exception as err:
            print(err)
            abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_questions(category_id):
        
        # get the category by id
        category = Category.query.filter_by(id = str(category_id)).one_or_none()
        # abort bad request(400) if the category is not found
        if category is None:
            abort(400)
         # get the matching questions for the specfifed category.id
        selection = Question.query.filter_by(category = str(category.id)).all()
        # paginate the results
        current_questions = paginate_questions(request, selection)

        # if len( current_questions) == 0:
        #     abort(404)

        return jsonify({
            'success': True,
            'questions':current_questions,
            'total_questions': len(current_questions),
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
            quiz_Category= body.get('quiz_category')
            previous_questions = body.get('previous_questions')
            category_id = quiz_Category['id']
            
            if (quiz_Category is None) or (previous_questions is None):
                abort(422) 

            if category_id == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(category = category_id).all()
            
            question = questions[random.randrange(0, len(questions), 1)]

            return jsonify({
                'success': True,
                'question': question.format()
            })
        except Exception as err:
            print(err)
            abort(400)

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


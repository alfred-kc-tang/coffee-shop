import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
from .database.models import *

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()
        return jsonify({
            'success': True, 
            'drinks': [drink.short() for drink in drinks]
        }), 200
    except:
        abort(404)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.all()
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        }), 200
    except:
        abort(404)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    req = dict(request.form or request.json or request.data)
    try:
        drink = Drink(title=req.get('title'), 
                      recipe=req.get('recipe') if isinstance(req.get('recipe'), str) else json.dumps(req.get('recipe')))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    
    except:
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, id):
    req = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)
    
    try:
        updated_title = req.get('title')
        updated_recipe = req.get('recipe')
        if updated_title:
            drink.title = updated_title
        if updated_recipe:
            drink.recipe = json.dumps(req['recipe'])
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)
    
    try:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': id
        })
    except:
        abort(422)


## Error Handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "bad request"
                    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found",
                    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
                    "success": False,
                    "error": 405,
                    "message": "method not allowed",
                    }), 405

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
                    "success": False,
                    "error": 500,
                    "message": "internal server error",
                    }), 500

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
                    "success": False,
                    "error": error.status_code,
                    "message": error.error['description'],
                    }), error.status_code

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "unauthorized"
                    }), 401

#!/usr/bin/python -B

# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Shopcart Service

Paths:
------
****** Shopcarts *******
GET /carts - Returns a list all of the Carts
GET /carts/{id} - Returns the Shopcart with a given id number
POST /carts - creates a new shopcart record in the database
PUT /carts/{id} - updates a Shopcart record in the database
DELETE /carts/{id} - deletes a Shopcart record in the database

****** Shopcart items *******
GET /carts/{id}/items - Returns a list all items of the Carts
GET /carts/{id}/items/{id} - Returns the Shopcart item with a given id number
POST /carts/{id}/items - creates a new shopcart item record in the database
PUT /carts/{id}/items/{id} - updates a Shopcart item record in the database
DELETE /carts/{id}/items/{id} - deletes a Shopcart item record in the database

****** ACTION on the resource ******
POST /carts/{id}/items/{id}/delete - Action to delete a shopcart item
"""

import sys
import logging
#from flask import Flask, Response, jsonify, request, json, url_for, make_response, abort
from flask import jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
# from flask_sqlalchemy import SQLAlchemy
from app.models import DataValidationError, ShoppingCart, ShoppingCartItems

# Import Flask application
from . import app

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_400_BAD_REQUEST,
                   error='Bad Request',
                   message=message), status.HTTP_400_BAD_REQUEST

@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_404_NOT_FOUND,
                   error='Not Found',
                   message=message), status.HTTP_404_NOT_FOUND

@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                   error='Method not Allowed',
                   message=message), status.HTTP_405_METHOD_NOT_ALLOWED

@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                   error='Unsupported media type',
                   message=message), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = error.message or str(error)
    app.logger.error(message)
    return jsonify(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                   error='Internal Server Error',
                   message=message), status.HTTP_500_INTERNAL_SERVER_ERROR


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return jsonify(name='Shopping cart REST API Service',
                   version='1.0',
                   paths=url_for('list_carts', _external=True)
                  ), status.HTTP_200_OK

######################################################################
# LIST ALL CARTS
######################################################################
@app.route('/carts', methods=['GET'])
def list_carts():
    """ Returns all of the Carts """
    if request.args.get('userId'):
        user_id = request.args.get('userId')
        app.logger.info('Getting Cart for user with id: {}'.format(user_id))
        results = ShoppingCart.find_by_user(user_id)
        if not results:
            raise NotFound('Cart with user id: {} was not found'.format(user_id))

        return jsonify([cart.serialize() for cart in results]), status.HTTP_200_OK
    elif request.args.get('state'):
        state = request.args.get('state')
        app.logger.info('Getting Carts with state: {}'.format(state))
        results = ShoppingCart.find_by_state(state)
        if not results:
            raise NotFound('Carts with state: {} was not found'.format(state))

        return jsonify([cart.serialize() for cart in results]), status.HTTP_200_OK
    else:
        results = []
        app.logger.info('Getting all Carts')
        results = ShoppingCart.all()
        return jsonify([cart.serialize() for cart in results]), status.HTTP_200_OK


######################################################################
# RETRIEVE A CART
######################################################################
@app.route('/carts/<int:cart_id>', methods=['GET'])
def get_carts(cart_id):
    """ Returns all of the Carts with given ID """
    app.logger.info('Getting Cart with id: {}'.format(cart_id))
    cart = ShoppingCart.find(cart_id)
    if not cart:
        raise NotFound('Cart with id: {} was not found'.format(cart_id))

    return jsonify(cart.serialize()), status.HTTP_200_OK


######################################################################
# ADD A NEW CART
######################################################################
@app.route('/carts', methods=['POST'])
def create_carts():
    """ Create a new Cart """
    app.logger.info('Create Cart requested')
    check_content_type('application/json')
    cart = ShoppingCart(None)
    cart.deserialize(request.get_json())
    cart.save()
    app.logger.info('Created Cart with id: {}'.format(cart.id))
    return make_response(jsonify(cart.serialize()),
                         status.HTTP_201_CREATED,
                         {'Location': url_for('get_carts', cart_id=cart.id, _external=True)})


######################################################################
# UPDATE AN EXISTING CART
######################################################################
@app.route('/carts/<int:cart_id>', methods=['PUT'])
def update_carts(cart_id):
    """ Update a cart with the given cart ID """
    app.logger.info('Updating cart with id: {}'.format(cart_id))
    check_content_type('application/json')
    cart = ShoppingCart.find(cart_id)
    if not cart:
        raise NotFound('Cart with id: {} was not found'.format(cart_id))

    # process the update request
    cart.deserialize(request.get_json())
    cart.id = cart_id # make id matches request
    cart.save()
    app.logger.info('Cart with id {} has been updated'.format(cart_id))
    return jsonify(cart.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A SHOPPING CART
######################################################################
@app.route('/carts/<int:cart_id>', methods=['DELETE'])
def delete_carts(cart_id):
    """ Deletes a Cart with given cart ID """
    app.logger.info('Request to delete cart with id: {}'.format(cart_id))
    cart = ShoppingCart.find(cart_id)
    if cart:
        cart.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)


######################################################################
# LIST ALL ITEMS of all CART
######################################################################
@app.route('/carts/items', methods=['GET'])
def list_items():
    """ Returns all of the Cart items """
    results = []
    app.logger.info('Getting all items of all cart')
    results = ShoppingCartItems.all()
    return jsonify([item.serialize() for item in results]), status.HTTP_200_OK


######################################################################
# RETRIEVE all ITEMS of A CART
######################################################################
@app.route('/carts/<int:cart_id>/items', methods=['GET'])
def get_items(cart_id):
    """ Returns all the items in a cart """
    app.logger.info('Getting items of Cart with id: {}'.format(cart_id))
    cart = ShoppingCart.find(cart_id)
    if not cart:
        raise NotFound('Cart with id: {} was not found'.format(cart_id))
    results = ShoppingCartItems.allItems(cart_id)
    if not results:
        raise NotFound('Cart with id: {} does not have any item'.format(cart_id))
    return jsonify([item.serialize() for item in results]), status.HTTP_200_OK


######################################################################
# RETRIEVE one particular ITEM of A CART
######################################################################
@app.route('/carts/<int:cart_id>/items/<int:item_id>', methods=['GET'])
def get_item(cart_id, item_id):
    app.logger.info('Getting particular item of id: {} in Cart with id: {}'.format(item_id, cart_id))
    cart = ShoppingCart.find(cart_id)
    if not cart:
        raise NotFound('Cart with id: {} was not found'.format(cart_id))
    results = ShoppingCartItems.find(cart_id, item_id)
    if not results:
        raise NotFound('Cart with id: {} does not have any item with id: {}'.format(cart_id, item_id))
    return jsonify([item.serialize() for item in results]), status.HTTP_200_OK


######################################################################
# ADD AN ITEM IN A CART
######################################################################
@app.route('/carts/<int:cart_id>/items', methods=['POST'])
def create_items(cart_id):
    app.logger.info('Create Item requested')
    cart = ShoppingCart.find(cart_id)
    if not cart:
        raise NotFound('No Cart with id: {} exist'.format(cart_id))
    item = ShoppingCartItems()
    item.deserialize(request.get_json())
    item.cartId = cart_id
    item.add()
    app.logger.info('Created Item with id: {}'.format(item.id))
    return make_response(jsonify(item.serialize()),
                         status.HTTP_201_CREATED,
                         {'Location': url_for('get_item', cart_id=cart_id, item_id=item.id, _external=True)})



######################################################################
# DELETE AN ITEM FROM A CART
######################################################################
@app.route('/carts/<int:cart_id>/items/<int:product_id>', methods=['DELETE'])
def delete_items(cart_id, product_id):
    app.logger.info('Request to delete item with id: {} from cart with id: {}'.format(product_id, cart_id))
    results = ShoppingCartItems.find(cart_id, product_id)
    if results:
        for item in results:
            item.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# ACTION TO DELETE AN ITEM FROM A CART
######################################################################
@app.route('/carts/<int:cart_id>/items/<int:item_id>/delete', methods=['POST'])
def action_to_delete_item(cart_id, item_id):
    app.logger.info('Action to delete item with id: {} from cart with id: {}'.format(item_id, cart_id))
    results = ShoppingCartItems.find(cart_id, item_id)
    if results:
        for item in results:
            item.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)



######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    ShoppingCart.init_db(app)
    ShoppingCartItems.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(415, 'Content-Type must be {}'.format(content_type))

def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print 'Setting up logging...'
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')

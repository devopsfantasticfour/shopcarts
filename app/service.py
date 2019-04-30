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
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from flask_restplus import Api, Resource, fields
import json
from werkzeug.exceptions import NotFound

from model import Shopcart, DataValidationError, DatabaseConnectionError

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route('/',methods=['GET'])
def index():
    """ Root URL response """
    return app.send_static_file('index.html')

######################################################################
# Special Error Handlers
######################################################################

@api.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
    """ Handles Database Errors from connection attempts """
    message = error.message or str(error)
    app.logger.critical(message)
    return {'status':500, 'error': 'Server Error', 'message': message}, 500



@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    api.logger("error handler")
    message = error.message or str(error)
    app.logger.info(message)
    #return {'status':400, 'error': 'Request Error', 'message': message}, 400
    api.abort(status.HTTP_400_BAD_REQUEST, "Shopcart ")


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route('/healthcheck')
def healthcheck():
    """ Let them know our heart is still beating """
    return make_response(jsonify(status=200, message='Healthy'), status.HTTP_200_OK)

######################################################################

######################################################################
#  PATH: /shopcarts/{user_id}
######################################################################
@ns.route('/<int:user_id>')
@ns.param('user_id','The User Identifier')
class ShopcartResource(Resource):
    """
    ShopcartResource class

    Allows the manipulation of a shopcart of a user
    GET /user{id} - Returns the list of the product in shopcart of a user with that user_id
    DELETE /user{id} - Deletes the list of the product in the shopcart of the user
    """


    #################################################################
    # GET THE LIST OF THE PRODUCT IN A USER'S SHOPCART
    #################################################################
    @ns.doc('get_shopcart_list')
    @ns.response(200, 'Success')
    @ns.response(404, 'Shopcart not found')
    @ns.marshal_list_with(shopcart_model)
    def get(self, user_id):
       """ Get the shopcart entry for user (user_id)
       This endpoint will show the list of products in user's shopcart from the database
       """
       app.logger.info("Request to get the list of the product in a user [%s]'s shopcart", user_id)
       shopcarts = []
       shopcarts = Shopcart.findByUserId(user_id)
       print(shopcarts.count())
       #if not shopcarts:
           #api.abort(status.HTTP_404_NOT_FOUND, "Shopcart with user_id '{}' was not found.".format(user_id))
       if shopcarts.count() == 0:
           api.abort(status.HTTP_404_NOT_FOUND, "Shopcart with user_id '{}' was not found.".format(user_id))
           #raise NotFound("Shopcart with user_id '{}' was not found.".format(user_id))
       results = [shopcart.serialize() for shopcart in shopcarts]
       return results, status.HTTP_200_OK

    ######################################################################
    # DELETE ALL PRODUCT OF USER
    ######################################################################
    @ns.doc('delete_user_shopcart')
    @ns.response(204, 'User Shopcart deleted')
    def delete(self, user_id):
       """
       Delete Product of User
       This endpoint will delete all Product of user based the user_id specified in the path
       """

       app.logger.info('Request to delete a shopcart of user id [%s]', user_id)
       shopcarts = Shopcart.findByUserId(user_id)
       if shopcarts:
          for shopcart in shopcarts:
              shopcart.delete()
       return '', status.HTTP_204_NO_CONTENT

##################################################################
# GET THE TOTAL AMOUNT OF ALL THE PRODUCTS IN SHOPCART
##################################################################
@ns.route('/<int:user_id>/total')
@ns.param('user_id','The User Identifier')
class ShopcartAction(Resource):

    """
    ShopcartAction class

    Allows to get the total amount of the user's shopcart for user(user_id)
    GET /user{id}/total - Returns the total amount of a user with that user_id
    """

    #################################################################
    # GET THE LIST OF THE PRODUCT IN A USER'S SHOPCART
    #################################################################
    @ns.doc('get_shopcart_total')
    @ns.response(200, 'Success')
    def get(self, user_id):
       """ Get the shopcart entry for user (user_id)
       This endpoint will show the total amount of the all items in the shopcart along with the list of items in user's shopcart 
       """

       app.logger.info("Request to get the total amount of a user [%s]'s shopcart", user_id)
       total_amount = 0.0
       shopcarts = Shopcart.findByUserId(user_id)
       for shopcart in shopcarts:
           total_amount = total_amount + (shopcart.price * shopcart.quantity)
       total_amount = round(total_amount, 2)

       inlist = [shopcart.serialize() for shopcart in shopcarts]

       dt = {'products':inlist,
             'total_price':total_amount}

       results = json.dumps(dt)
       return make_response(results, status.HTTP_200_OK)

######################################################################
#  PATH: /shopcarts/<int:user_id>/product/<int:product_id>
######################################################################
@ns.route('/<int:user_id>/product/<int:product_id>', strict_slashes=False)
class ProductResource(Resource):

    """
    ProductResource class

    Allows the manipulation of products in user's a Shopcart
    GET /user{id}/product/product{id} - Retrieves given product from given user's shopcart
    DELETE /user{id}/product/product{id} -  Deletes given product from given user's shopcart
    """
    #------------------------------------------------------------------
    # RETRIEVES A PRODUCT FROM USER'S SHOPCART
    #------------------------------------------------------------------
    @ns.doc('get_product')
    @ns.response(200, 'Success')
    @ns.response(404, 'Product not found')
    @ns.marshal_with(shopcart_model)

    def get(self, user_id, product_id):
        """
        Retrieve a product from user's shopcart

        This endpoint will return a product having given product_id from user having given user_id
        """
        app.logger.info("Request to Retrieve a product with id [%s] from shopcart of user with id [%s]", product_id, user_id)
        result = Shopcart.find(user_id, product_id)
        if not result:
            raise NotFound("User with id '{uid}' doesn't have product with id '{pid}' was not found.' in the shopcart ".format(uid = user_id, pid = product_id))
        return result.serialize(),status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETES A PRODUCT FROM USER'S SHOPCART
    #------------------------------------------------------------------
    @ns.doc('delete_product')
    @ns.response(204, 'Product deleted')
    def delete(self, user_id, product_id):
        """
        Delete a product from a user's shopcart

        This endpoint will delete a product based the id of product and user specified in the path
        """
        app.logger.info('Request to Delete a product with id [%s] from user with id [%s]', user_id, product_id)
        shopcart = Shopcart.find(user_id, product_id)
        if shopcart:
            shopcart.delete()
        return '', status.HTTP_204_NO_CONTENT


    #------------------------------------------------------------------
    # UPDATE A PRODUCT IN USER'S SHOPCART
    #------------------------------------------------------------------
    @ns.doc('update_product')
    @ns.response(200, 'Success')
    @ns.response(404, 'Product not found')
    @ns.response(400, 'The posted Product data was not valid')
    @ns.expect(shopcart_model)
    @ns.marshal_with(shopcart_model)
    def put(self, user_id, product_id):
        """
        Update a Shopcart entry specific to that user_id and product_id
        This endpoint will update a Shopcart based the data in the body that is posted
        """
        app.logger.info('Request to Update a product with id [%s] from user with id [%s]', user_id, product_id)
        check_content_type('application/json')
        shopcart = Shopcart.find(user_id, product_id)
        if not shopcart:
            raise NotFound("User with id '{uid}' doesn't have product with id '{pid}' was not found.' in the shopcart ".format(uid = user_id, pid = product_id))

        data = api.payload
        app.logger.info(data)
        shopcart.deserialize(data)
        q = 0
        try:
           q = int(shopcart.quantity)
        except ValueError:
                app.logger.info("value error")
                abort(status.HTTP_400_BAD_REQUEST, 'Quantity parameter is not valid: {}'.format(shopcart.quantity))

        if q < 1:
            app.logger.info("Added quantity is 0")
            abort(status.HTTP_400_BAD_REQUEST, 'You should input number more than 0 for quantity to add a product')

        shopcart.user_id = user_id
        shopcart.product_id = product_id
        shopcart.save()
        return shopcart.serialize(), status.HTTP_200_OK

######################################################################
#  PATH: /shopcarts
######################################################################
@ns.route('/', strict_slashes=False)
class ShopcartCollection(Resource):

    """ Handles all interactions with collections of Shopcarts """
    #------------------------------------------------------------------
    # LIST ALL SHOPCARTS
    #------------------------------------------------------------------
    @ns.doc('list_shopcarts')
    @ns.response(200, 'Success')
    #@ns.param('category', 'List Shopcarts grouped by user_id')
    def get(self):
        """ 
        Returns all of the Shopcarts grouped by user_id 
        This endpoint will give the information of all shopcart of all users
        """

        app.logger.info('Request to list Shopcarts...')

        users = Shopcart.list_users();
        results = ''
        #res = []
        for user_id in users:
            inlist = Shopcart.findByUserId(user_id)
            dt = []
            for item in inlist:
                tmp2 = {"product_id":item.product_id,
                        "price": item.price,
                        "quantity": item.quantity}
                dt.append(tmp2)
            tmp = {"user_id":user_id,
                   "products":dt}
            if len(results)>1: 
                results += ","
            results += json.dumps(tmp)
        #res.append()
        #res.append(results)
        res = "["+results+"]"
        return make_response(res, status.HTTP_200_OK)

    #------------------------------------------------------------------
    # ADD A NEW PRODUCT
    #------------------------------------------------------------------
    @ns.doc('add_product')
    @ns.expect(shopcart_model)
    @ns.response(400, 'The posted data was not valid')
    @ns.response(201, 'Product added successfully')
    @ns.marshal_with(shopcart_model, code=201)
    def post(self):
        """
        add a product to a shopcart
        This endpoint will add a new item to a user's shopcart
        """
        app.logger.info('Request to Add an Item to Shopcart')
        check_content_type('application/json')
        shopcart = Shopcart()
        app.logger.info('Payload = %s', api.payload)
        shopcart.deserialize(api.payload)

        q = 0;
        try:
            q = int(shopcart.quantity)
        except ValueError:
                app.logger.info("value error")
                #raise DataValidationError
                abort(status.HTTP_400_BAD_REQUEST, 'Quantity parameter is not valid: {}'.format(shopcart.quantity))

        if shopcart.user_id is None or shopcart.user_id == '' or shopcart.product_id is None or shopcart.product_id =='' \
            or shopcart.price is None or shopcart.price == '' or shopcart.quantity is None or shopcart.quantity == '':
            app.logger.info("some parameter is none")
            abort(status.HTTP_400_BAD_REQUEST, 'Some data is missing in the request')
        elif q < 1:
            app.logger.info("Added quantity is 0")
            abort(status.HTTP_400_BAD_REQUEST, 'You should input number more than 0 for quantity to add a product')
        else:
            #Check if the entry exists, if yes then increase quantity of product
            exists = Shopcart.find(shopcart.user_id, shopcart.product_id)
            if exists:
                exists.quantity = exists.quantity + q
                exists.save()
                shopcart = exists

            shopcart.save()

            app.logger.info('Item with new id [%s] saved to shopcart of user [%s]!', shopcart.user_id, shopcart.product_id)
            location_url = api.url_for(ProductResource,  user_id=shopcart.user_id, product_id=shopcart.product_id, _external=True)
            return shopcart.serialize(), status.HTTP_201_CREATED, {'Location': location_url}


######################################################################
#  PATH: /shopcarts/users
######################################################################
@ns.route('/users')
class ShopcartUsersResource(Resource):
    """
    ShopcartUsersResource class

    Allows getting the list of the users whose shopcarts worth more than given amount
    GET /users - Returns the list of the users whose shopcarts' total is more than a certain amount
    """
    @ns.param('amount', 'amount for searching')

    ############################################################################
    # QUERY DATABASE FOR SHOPCARTS HAVING PRODUCTS WORTH MORE THAN GIVEN AMOUNT
    ############################################################################
    @ns.doc('get_users_with_shopcart_more_than_given_amount')
    @ns.response(200, 'Sucess')
    @ns.response(400, 'parameter amount not found')
    def get(self):
        """
        Get the shopcart list of users
        This endpoint will show the list of the user shopcart list
        with amount more than given amount
        """
        amount = request.args.get('amount');
        app.logger.info("Request to get the list of the user shopcart having more than {}".format(amount))

        if amount is None:
            app.logger.info("amount is none")
            abort(status.HTTP_400_BAD_REQUEST, 'parameter amount not found')
        else:
            try:
                app.logger.info("try start")
                amount = float(amount)
                app.logger.info("try end")
            except ValueError:
                app.logger.info("value error")
                abort(status.HTTP_400_BAD_REQUEST, 'parameter is not valid: {}'.format(amount))
        users = Shopcart.find_users_by_shopcart_amount(amount)
        app.logger.info("get data")
        return users, status.HTTP_200_OK


#####################################################################
# DELETE ALL SHOPCARTS DATA (for testing only)
######################################################################
@app.route('/shopcarts/reset', methods=['DELETE'])
def shopcarts_reset():
    """ Clears all items from shopcarts for all users from the database 
    This endpoint will remove all the shopcart information in the server
    """
    Shopcart.remove_all()
    return '', status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

@app.before_first_request
def init_db():
    """ Initlaize the SQLAlchemy app"""
    Shopcart.init_db()

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Content-Type must be {}'.format(content_type))

#@app.before_first_request
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

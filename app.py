
import os
import sys
import logging
from flask import Flask, Response, jsonify, request, json, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')
DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db/development.db')

# Create Flask application
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
app.config['LOGGING_LEVEL'] = logging.INFO

db = SQLAlchemy(app)


######################################################################
# Custom Exceptions
######################################################################
class DataValidationError(ValueError):
    pass

######################################################################
# ERROR Handling
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    message = str(error)
    app.logger.info(message)
    return jsonify(status=400, error='Bad Request', message=message), \
                   status.HTTP_400_BAD_REQUEST

@app.errorhandler(404)
def not_found(error):
    message = str(error)
    app.logger.info(message)
    return jsonify(status=404, error='Not Found', message=message), \
                   status.HTTP_404_NOT_FOUND

@app.errorhandler(400)
def bad_request(error):
    message = str(error)
    app.logger.info(message)
    return jsonify(status=400, error='Bad Request', message=message), \
                   status.HTTP_400_BAD_REQUEST

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(status=405, error='Method not Allowed',
                   message='Your request method is not supported. Check your HTTP method and try again.'), \
                   status.HTTP_405_METHOD_NOT_ALLOWED

@app.errorhandler(500)
def internal_error(error):
    return jsonify(status=500, error='Internal Server Error',
                   message='Houston... we have a problem.'), \
                   status.HTTP_500_INTERNAL_SERVER_ERROR

#Shopping cart model for DATABASE_URI
class ShoppingCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer())

    def __init__(self, userId = 0):
        self.userId = userId

    def save(self):
        """ Saves an existing shopping cart in the database """
        # if the id is None it hasn't been added to the database
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Deletes a shopping cart from the database """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return { "id": self.id, "userId": self.userId }

    def deserialize(self, data):
        try:
            self.userId = data['userId']
        except KeyError as e:
            raise DataValidationError('Invalid cart: missing ' + e.args[0])
        except TypeError as e:
            raise DataValidationError('Invalid cart: body of request contained bad or no data')
        return self

    @classmethod
    def all(cls):
        """ Returns all of the carts in the database """
        return cls.query.all()

    @classmethod
    def find(cls, cart_id):
        """ Finds a cart by it's ID """
        return cls.query.get(cart_id)


class ShoppingCartItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    productID = db.Column(db.Integer)
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    cartId = db.Column(db.Integer)

    def __init__(self, productID = 0, price = 0.0, quantity = 0, cartId = 0):
        self.productID = productID
        self.price = price
        self.quantity = quantity
        self.cartId = cartId

    def add(self):
        """ Adds an item to shopping cart """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Deletes an item from shopping cart """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return { "id": self.id,
                "productID": self.productID,
                "price": self.price,
                "quantity": self.quantity,
                "cartId": self.cartId
                }

    def deserialize(self, data):
        try:
            self.productID = data['productID']
            self.price = data['price']
            self.quantity = data['quantity']
            self.cartId = data['cartId']
        except KeyError as e:
            raise DataValidationError('Invalid item: missing ' + e.args[0])
        except TypeError as e:
            raise DataValidationError('Invalid item: body of request contained bad or no data')
        return self

    @classmethod
    def all(cls):
        """ Returns all of the items in the cart database """
        return cls.query.all()

    @classmethod
    def allItems(cls, cart_ID):
        """ Returns all of the items for a particular cart ID """
        return cls.query.filter(cls.cartId == cart_ID).all()

    @classmethod
    def find(cls, cart_ID, product_ID):
        """ Finds an item in a particular cart  """
        return cls.query.filter(cls.cartId == cart_ID, cls.productID == product_ID).all()


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    return jsonify(name='Shopping cart REST API Service',
                   version='1.0',
                   url=url_for('list_carts', _external=True)), status.HTTP_200_OK

######################################################################
# LIST ALL Carts
######################################################################
@app.route('/carts', methods=['GET'])
def list_carts():
    results = []
    app.logger.info('Getting all Carts')
    results = ShoppingCart.all()
    return jsonify([cart.serialize() for cart in results]), status.HTTP_200_OK


######################################################################
# RETRIEVE A CART
######################################################################
@app.route('/carts/<int:cart_id>', methods=['GET'])
def get_carts(cart_id):
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
    app.logger.info('Create Cart requested')
    cart = ShoppingCart(None)
    cart.deserialize(request.get_json())
    cart.save()
    app.logger.info('Created Cart with id: {}'.format(cart.id))
    return make_response(jsonify(cart.serialize()),
                         status.HTTP_201_CREATED,
                         {'Location': url_for('get_carts', cart_id=cart.id, _external=True)})

######################################################################
# LIST ALL ITEMS of all CART
######################################################################
@app.route('/carts/items', methods=['GET'])
def list_items():
    results = []
    app.logger.info('Getting all items of all cart')
    results = ShoppingCartItems.all()
    return jsonify([item.serialize() for item in results]), status.HTTP_200_OK


######################################################################
# RETRIEVE all ITEMS of A CART
######################################################################
@app.route('/carts/<int:cart_id>/items', methods=['GET'])
def get_items(cart_id):
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
@app.route('/carts/<int:cart_id>/items/<int:product_id>', methods=['GET'])
def get_item(cart_id, product_id):
    app.logger.info('Getting particular item of id: {} in Cart with id: {}'.format(product_id, cart_id))
    cart = ShoppingCart.find(cart_id)
    if not cart:
        raise NotFound('Cart with id: {} was not found'.format(cart_id))
    results = ShoppingCartItems.find(cart_id, product_id)
    if not results:
        raise NotFound('Cart with id: {} does not have any item with id: {}'.format(cart_id, product_id))
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
                         {'Location': url_for('get_item', cart_id=cart_id, product_id=item.id, _external=True)})



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
# DELETE A SHOPPING CART
######################################################################
@app.route('/carts/<int:cart_id>', methods=['DELETE'])
def delete_carts(cart_id):
    app.logger.info('Request to delete cart with id: {}'.format(cart_id))
    cart = ShoppingCart.find(cart_id)
    if cart:
        cart.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)



@app.before_first_request
def initialize():
    db.create_all()  # make our sqlalchemy tables



# main
if __name__ == "__main__":
    print "Shopping cart Service Starting..."
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)

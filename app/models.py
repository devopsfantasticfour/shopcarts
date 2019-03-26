#!/usr/bin/python -B

# Copyright 2016, 2017 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Models for Shopcart Service

All of the models are stored in this module

Models
------
ShoppingCart - A shopcart used in the ecommerce Store
ShoppingCartItems - A shopcart item used in the shopcart

Attributes:
-----------
AGGGGGGG - Modify these
name (string) - the name of the pet
category (string) - the category the pet belongs to (i.e., dog, cat)
available (boolean) - True for pets that are available for adoption

"""
import logging
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class ShoppingCart(db.Model):
    """
    Class that represents a Shopping Cart

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    logger = logging.getLogger(__name__)
    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer())
    state = db.Column(db.String(20))

    def __init__(self, userId = 0, state = "empty"):
        self.userId = userId
        self.state = state
        
    def __repr__(self):
        return '<ShoppingCart %r>' % (self.name)

    def save(self):
        """
        Saves a ShoppingCart to the data store
        """
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Removes a shopping cart from the data store """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Shopping Cart into a dictionary """
        return { "id": self.id, 
        		 "userId": self.userId, 
        		 "state": self.state }

    def deserialize(self, data):
        """
        Deserializes a Shopping Cart from a dictionary

        Args:
            data (dict): A dictionary containing the Shopping Cart data
        """
        try:
            self.userId = data['userId']
            self.state = data['state']
        except KeyError as e:
            raise DataValidationError('Invalid cart: missing ' + e.args[0])
        except TypeError as e:
            raise DataValidationError('Invalid cart: body of request contained bad or no data')
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Carts in the database """
        cls.logger.info('Processing all Carts')
        return cls.query.all()
        
    @classmethod
    def find(cls, cart_id):
        """ Finds a Cart by cart ID """
        cls.logger.info('Processing lookup for id %s ...', cart_id)
        return cls.query.get(cart_id)
            	
    @classmethod
    def find_or_404(cls, cart_id):
        """ Find a Cart by its id """
        cls.logger.info('Processing lookup or 404 for id %s ...', cart_id)
        return cls.query.get_or_404(cart_id)

    @classmethod
    def find_by_user(cls, user_id):
        """ Finds a cart by user's ID """
        return cls.query.filter(cls.userId == user_id).all()

    @classmethod
    def find_by_state(cls, state):
        """ Finds a cart by its state """
        return cls.query.filter(cls.state == state).all()
        
###################################################
# SHOPPING CART ITEMS MODEL
###################################################
class ShoppingCartItems(db.Model):

    """
    Class that represents a Shopcart item

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    logger = logging.getLogger(__name__)
    app = None

    # Table Schema
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

    def __repr__(self):
        return '<CartItem %r>' % (self.name)
        
    def add(self):
        """ Adds an item to shopping cart """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Deletes an item from shopping cart """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes an item into a dictionary """
        return { "id": self.id,
                "productID": self.productID,
                "price": self.price,
                "quantity": self.quantity,
                "cartId": self.cartId
                }

    def deserialize(self, data):
        """
        Deserializes an item from a dictionary

        Args:
            data (dict): A dictionary containing the Item data
        """
        try:
            self.productID = data['productID']
            self.price = data['price']
            self.quantity = data['quantity']
            self.cartId = data['cartId']
            self.id = data['id']
        except KeyError as e:
            raise DataValidationError('Invalid item: missing ' + e.args[0])
        except TypeError as e:
            raise DataValidationError('Invalid item: body of request contained bad or no data')
        return self
    
    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the items in the cart database """
        cls.logger.info('Processing all Items')
        return cls.query.all()

    @classmethod
    def allItems(cls, cart_ID):
        """ Returns all of the items for a particular cart ID """
        return cls.query.filter(cls.cartId == cart_ID).all()

    @classmethod
    def find(cls, item_ID):
        """ Finds an item in a particular cart  """
        return cls.query.filter(cls.id == item_ID).all()


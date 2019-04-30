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
Shopcart - A Shopcart used by each User

Attributes:
-----------
product_id (int)    - the product-id of a Product used to uniquely identify it
user_id (int)       - the user-id of the User which uniquely identifies the User
quantity (int)     - number of items User wants to buy of that particular product
price(float)       - cost of one item of the Product

"""
import os
import json
import logging
from . import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.sql import label

######################################################################
# Custom Exceptions
######################################################################
class DataValidationError(ValueError):
    pass

class DatabaseConnectionError(OSError):
    pass

class Shopcart(db.Model):
    """
    Class that represents a Shopcart

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    logger = logging.getLogger(__name__)

    # Table Schema
    user_id = db.Column(db.Integer,primary_key=True)
    product_id = db.Column(db.Integer,primary_key=True)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

    def save(self):
        """
        Saves a Shopcart to the data store
        """
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Shopcart entry into a dictionary """
        return {"user_id": self.user_id,
                "product_id": self.product_id,
                "quantity": self.quantity,
                "price": self.price}

    def deserialize(self, data):
        """
        Deserializes a Shopcart entry from a dictionary

        Args:
            data (dict): A dictionary containing the Shopcart entry data
        """
        try:
            self.user_id = data['user_id']
            self.product_id = data['product_id']
            self.quantity = data['quantity']
            self.price = data['price']
        except KeyError as error:
            raise DataValidationError('Invalid entry for Shopcart: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid entry for Shopcart: body of request contained' \
                                      'bad or no data')
        return self


    def delete(self):
        """ Removes a Shopcart from the data store """
        db.session.delete(self)
        db.session.commit()

######################################################################
#  F I N D E R   M E T H O D S
######################################################################

    @staticmethod
    def list_users():
        """ List all user in table """
       # users = (db.session.query(Shopcart.user_id).distinct()).all();
        users = []
        for user in db.session.query(Shopcart.user_id).distinct():
            users.append(user.user_id)
        return users


    @staticmethod
    def find(user_id, product_id):
        """ Finds if user <user_id> has product <product_id> by it's ID """
        Shopcart.logger.info('Processing lookup for user id %s and product id %s ...', user_id, product_id)
        return Shopcart.query.get((user_id,product_id))

    @staticmethod
    def findByUserId(user_id):
        """ Finds the list of product in the shopcart of user by <user_id> """
        Shopcart.logger.info('Processing lookup for id %s ...', user_id)
        return Shopcart.query.filter(Shopcart.user_id == user_id)

    @staticmethod
    def find_users_by_shopcart_amount(amount):
        """ Finds the list of users who have in their shopcarts good worth 'amount' or more """
        results = db.session.query(Shopcart.user_id, label('total_amount', func.sum(Shopcart.price*Shopcart.quantity))).group_by(Shopcart.user_id).all();
        users = []
        for result in results:
            #Shopcart.logger.info("Result "+ str(result.user_id) +"total_amount " + str(result.total_amount) + str(float(result.total_amount) >= float(amount)))
            if float(result.total_amount) >= float(amount):
                users.append(result.user_id)

        return users


######################################################################
#  S T A T I C   D A T A B A S E   M E T H O D S
######################################################################
    @staticmethod
    def remove_all():
        """ Removes all entries in shopcarts for all users from the database """
        db.session.query(Shopcart).delete()
        db.session.commit()


    @staticmethod
    def all():
        """ Returns all of the Shopcarts in the database """
        Shopcart.logger.info('Processing all Shopcarts')
        return Shopcart.query.all()


######################################################################
#  D A T A B A S E   C O N N E C T I O N   M E T H O D S
######################################################################
    @staticmethod
    def init_db():
        """ Initializes the database session """
        Shopcart.logger.info('Initializing database')
        db.create_all()  # make our sqlalchemy tables

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
Test cases for ShoppingCart Model

Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import os
from app.models import DataValidationError, db, ShoppingCart, ShoppingCartItems
from app import app

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestShoppingCarts(unittest.TestCase):
    """ Test Cases for Shopping Carts """

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.debug = False
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        ShoppingCart.init_db(app)
        db.drop_all()    # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_a_shopcart(self):
        """ Create a cart and assert that it exists """
        shopcart = ShoppingCart(state="activated", userId=5)
        self.assertTrue(shopcart != None)
        self.assertEqual(shopcart.id, None)
        self.assertEqual(shopcart.state, "activated")
        self.assertEqual(shopcart.userId, 5)

    def test_add_a_cart(self):
        """ Create a cart and add it to the database """
        shopcarts = ShoppingCart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShoppingCart(state="activated", userId=5)
        self.assertTrue(shopcart != None)
        self.assertEqual(shopcart.id, None)
        shopcart.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(shopcart.id, 1)
        shopcarts = ShoppingCart.all()
        self.assertEqual(len(shopcarts), 1)

    def test_update_a_cart(self):
        """ Update a ShopCart """
        shopcart = ShoppingCart(state="activated", userId=5)
        shopcart.save()
        self.assertEqual(shopcart.id, 1)
        # Change it an save it
        shopcart.state = "deactivated"
        shopcart.save()
        self.assertEqual(shopcart.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        shopcarts = ShoppingCart.all()
        self.assertEqual(len(shopcarts), 1)
        self.assertEqual(shopcarts[0].state, "deactivated")

    def test_delete_a_cart(self):
        """ Delete a Cart """
        shopcart = ShoppingCart(state="activated", userId=5)
        shopcart.save()
        self.assertEqual(len(ShoppingCart.all()), 1)
        # delete the cart and make sure it isn't in the database
        shopcart.delete()
        self.assertEqual(len(ShoppingCart.all()), 0)

    def test_serialize_a_cart(self):
        """ Test serialization of a Cart """
        shopcart = ShoppingCart(state="deactivated", userId=10)
        data = shopcart.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], None)
        self.assertIn('state', data)
        self.assertEqual(data['state'], "deactivated")
        self.assertIn('userId', data)
        self.assertEqual(data['userId'], 10)

    def test_deserialize_a_cart(self):
        """ Test deserialization of a Cart """
        data = {"id": 1, "state": "deactivated", "userId": 15}
        shopcart = ShoppingCart()
        shopcart.deserialize(data)
        self.assertNotEqual(shopcart, None)
        self.assertEqual(shopcart.id, None)
        self.assertEqual(shopcart.state, "deactivated")
        self.assertEqual(shopcart.userId, 15)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        shopcart = ShoppingCart()
        self.assertRaises(DataValidationError, shopcart.deserialize, data)

    def test_find_cart(self):
        """ Find a Cart by ID """
        ShoppingCart(state="activated", userId=7).save()
        deactivated = ShoppingCart(state="deactivated", userId=8)
        deactivated.save()
        shopcart = ShoppingCart.find(deactivated.id)
        self.assertIsNot(shopcart, None)
        self.assertEqual(shopcart.id, deactivated.id)
        self.assertEqual(shopcart.state, "deactivated")
        self.assertEqual(shopcart.userId, 8)

    def test_find_by_state(self):
        """ Find Carts by State """
        ShoppingCart(state="activated", userId=4).save()
        ShoppingCart(state="deactivated", userId=5).save()
        shopcarts = ShoppingCart.find_by_state("deactivated")
        self.assertEqual(shopcarts[0].state, "deactivated")
        self.assertEqual(shopcarts[0].userId, 5)

    def test_find_by_user(self):
        """ Find a Cart by UserId """
        ShoppingCart(state="activated", userId=4).save()
        ShoppingCart(state="deactivated", userId=5).save()
        shopcarts = ShoppingCart.find_by_user(5)
        self.assertEqual(shopcarts[0].state, "deactivated")
        self.assertEqual(shopcarts[0].userId, 5)


######################################################################
#  T E S T   C A S E S
######################################################################
class TestShoppingCartItems(unittest.TestCase):
    """ Test Cases for Shopping Cart Items """

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.debug = False
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        ShoppingCartItems.init_db(app)
        db.drop_all()    # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_a_shopcartitem(self):
        """ Create a cart and assert that it exists """
        item = ShoppingCartItems(productID=1234, price=12.99, quantity=1, cartId=5)
        self.assertTrue(item != None)
        self.assertEqual(item.id, None)
        self.assertEqual(item.productID, 1234)
        self.assertEqual(item.price, 12.99)
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.cartId, 5)

    def test_add_a_shopcartitem(self):
        """ Create an item and add it to the database """
        items = ShoppingCartItems.all()
        self.assertEqual(items, [])
        item = ShoppingCartItems(productID=1234, price=12.99, quantity=1, cartId=5)
        self.assertTrue(item != None)
        self.assertEqual(item.id, None)
        item.add()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(item.id, 1)
        items = ShoppingCartItems.all()
        self.assertEqual(len(items), 1)

    def test_update_a_shopcartitem(self):
        """ Update a ShopCart Item"""
        item = ShoppingCartItems(productID=1234, price=12.99, quantity=1, cartId=5)
        item.add()
        self.assertEqual(item.id, 1)
        # Change it and save it
        item.productID = 4321
        item.add()
        self.assertEqual(item.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        items = ShoppingCartItems.all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].productID, 4321)

    def test_delete_a_shopcartitem(self):
        """ Delete a Cart Item """
        item = ShoppingCartItems(productID=1234, price=12.99, quantity=1, cartId=5)
        item.add()
        self.assertEqual(len(ShoppingCartItems.all()), 1)
        # delete the cart item and make sure it isn't in the database
        item.delete()
        self.assertEqual(len(ShoppingCartItems.all()), 0)

    def test_serialize_a_shopcartitem(self):
        """ Test serialization of a Cart Item """
        item = ShoppingCartItems(productID=1234, price=12.99, quantity=1, cartId=5)
        data = item.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], None)
        self.assertIn('productID', data)
        self.assertEqual(data['productID'], 1234)
        self.assertIn('price', data)
        self.assertEqual(data['price'], 12.99)
        self.assertIn('quantity', data)
        self.assertEqual(data['quantity'], 1)
        self.assertIn('cartId', data)
        self.assertEqual(data['cartId'], 5)

    def test_deserialize_a_shopcartitem(self):
        """ Test deserialization of a Cart Item """
        data = {"id": 1, "productID": 1234, "price": 12.99, "quantity" : 1, "cartId": 5}
        item = ShoppingCartItems()
        item.deserialize(data)
        self.assertNotEqual(item, None)
        self.assertEqual(item.productID, 1234)
        self.assertEqual(item.price, 12.99)
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.cartId, 5)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a ctionary"
        item = ShoppingCartItems()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_find_by_cartId(self):
        """ Find all items for a particular CartId """
        ShoppingCartItems(productID=1234, price=12.99, quantity=1, cartId=5).add()
        ShoppingCartItems(productID=4321, price=18.99, quantity=2, cartId=8).add()
        items = ShoppingCartItems.allItems(8)
        self.assertEqual(items[0].productID, 4321)
        self.assertEqual(items[0].price, 18.99)
        self.assertEqual(items[0].quantity, 2)
        self.assertEqual(items[0].cartId, 8)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()

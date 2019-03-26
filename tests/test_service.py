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
Shop Carts API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""

import unittest
import os
import logging
from flask_api import status    # HTTP Status Codes
#from mock import MagicMock, patch
from app.models import DataValidationError, db, ShoppingCart, ShoppingCartItems
import app.service as service
from .cart_factory import ShoppingCartFactory, ShoppingCartItemsFactory

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestShoppingCartServer(unittest.TestCase):
    """ Shop Carts Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        service.app.debug = False
        service.initialize_logging(logging.INFO)
        # Set up the test database
        service.app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        service.init_db()
        db.drop_all()    # clean up the last tests
        db.create_all()  # create new tables
        self.app = service.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_carts(self, count):
        """ Factory method to create carts in bulk """
        carts = []
        for _ in range(count):
            test_cart = ShoppingCartFactory()
            resp = self.app.post('/carts',
                                 json=test_cart.serialize(),
                                 content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED, 'Could not create test cart')
            new_cart = resp.get_json()
            test_cart.id = new_cart['id']
            carts.append(test_cart)
        return carts

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], 'Shopping cart REST API Service')

    def test_get_cart_list(self):
        """ Get a list of Carts """
        self._create_carts(5)
        resp = self.app.get('/carts')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_cart(self):
        """ Get a single Cart """
        # get the id of a cart
        test_cart = self._create_carts(1)[0]
        resp = self.app.get('/carts/{}'.format(test_cart.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['state'], test_cart.state)

    def test_get_cart_not_found(self):
        """ Get a Cart thats not found """
        resp = self.app.get('/carts/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_cart(self):
        """ Create a new Cart """
        test_cart = ShoppingCartFactory()
        resp = self.app.post('/carts',
                             json=test_cart.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue(location != None)
        # Check the data is correct
        new_cart = resp.get_json()
        self.assertEqual(new_cart['state'], test_cart.state, "State does not match")
        self.assertEqual(new_cart['userId'], test_cart.userId, "UserId does not match")
        # Check that the location header was correct
        resp = self.app.get(location,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_cart = resp.get_json()
        self.assertEqual(new_cart['state'], test_cart.state, "State does not match")
        self.assertEqual(new_cart['userId'], test_cart.userId, "UserId does not match")

    def test_update_cart(self):
        """ Update an existing Cart """
        # create a cart to update
        test_cart = ShoppingCartFactory()
        resp = self.app.post('/carts',
                             json=test_cart.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the cart
        new_cart = resp.get_json()
        new_cart['userId'] = 5555
        resp = self.app.put('/carts/{}'.format(new_cart['id']),
                            json=new_cart,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_cart = resp.get_json()
        self.assertEqual(updated_cart['userId'], 5555)

    def test_delete_cart(self):
        """ Delete a Cart """
        test_cart = self._create_carts(1)[0]
        resp = self.app.delete('/carts/{}'.format(test_cart.id),
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get('/carts/{}'.format(test_cart.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_cart_list_by_state(self):
        """ Query Carts by state """
        carts = self._create_carts(10)
        test_state = carts[0].state
        state_carts = [cart for cart in carts if cart.state == test_state]
        resp = self.app.get('/carts',
                            query_string='state={}'.format(test_state))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(state_carts))
        # check the data just to be sure
        for cart in data:
            self.assertEqual(cart['state'], test_state)

    def test_query_cart_list_by_userId(self):
        """ Query Carts by userId """
        carts = self._create_carts(10)
        test_userId = carts[0].userId
        userId_carts = [cart for cart in carts if cart.userId == test_userId]
        resp = self.app.get('/carts',
                            query_string='userId={}'.format(test_userId))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(userId_carts))
        # check the data just to be sure
        for cart in data:
            self.assertEqual(cart['userId'], test_userId)


    # @patch('app.service.Pet.find_by_name')
    # def test_bad_request(self, bad_request_mock):
    #     """ Test a Bad Request error from Find By Name """
    #     bad_request_mock.side_effect = DataValidationError()
    #     resp = self.app.get('/pets', query_string='name=fido')
    #     self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    #
    # @patch('app.service.Pet.find_by_name')
    # def test_mock_search_data(self, pet_find_mock):
    #     """ Test showing how to mock data """
    #     pet_find_mock.return_value = [MagicMock(serialize=lambda: {'name': 'fido'})]
    #     resp = self.app.get('/pets', query_string='name=fido')
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()

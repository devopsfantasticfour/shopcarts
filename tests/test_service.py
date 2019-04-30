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
Shopcart API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""
import unittest
import os
import json
import logging
from flask_api import status    # HTTP Status Codes
from mock import MagicMock, patch
from werkzeug.exceptions import NotFound,BadRequest
from app.model import Shopcart, DataValidationError, db
import app.vcap_services as vcap
import app.service as service
from app.service import app

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_409_CONFLICT = 409
HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415


DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestShopcartServer(unittest.TestCase):
    """ Shopcart Server Tests """

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
        Shopcart(user_id=1, product_id=1, quantity=1, price=12.00).save()
        Shopcart(user_id=1, product_id=2, quantity=1, price=15.00).save()
        self.app = service.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    # FlaskRESTPlus takes over the index so we can't test it
    def test_index(self):
        """ Test the index page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertIn('Shopcarts REST API Service', resp.data)

    
    def test_health_check(self):
        """ Test /healthcheck """
        resp = self.app.get("/healthcheck")
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertIn('Healthy', resp.data)



    def test_create_shopcart_entry_new_product(self):
        """ Create a new Shopcart entry - add new product"""

        #Get number of products in users shopcart
        product_count = self.get_product_count(2)


        # check if the required data is missing
        new_prod = dict(user_id='',product_id=1, quantity=1, price=12.00)
        data = json.dumps(new_prod)
        resp = self.app.post('/shopcarts',
                              data=data,
                              content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        new_prod = dict(user_id=1, product_id=1, quantity='a', price=12.00)
        data = json.dumps(new_prod)
        resp = self.app.post('/shopcarts',
                              data=data,
                              content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)



        new_prod = dict(user_id=1, product_id=1, quantity=0, price=12.00)
        data = json.dumps(new_prod)
        resp = self.app.post('/shopcarts',
                              data=data,
                              content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


        # add a new product to shopcart of user
        new_product = dict(user_id=2, product_id=1, quantity=1, price=12.00)
        data = json.dumps(new_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        #Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['user_id'], 2)
        self.assertEqual(new_json['product_id'], 1)

        # check that count has gone up and includes sammy
        resp = self.app.get('/shopcarts/2')

        # print 'resp_data(2): ' + resp.data
        data = json.loads(resp.data)
        print(data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(new_json, data)
        self.assertEqual(len(data), product_count + 1)

    def test_list_shop_cart_entry_by_user_id(self):
        """ Query shopcart by user_id """
        shopcart = Shopcart.findByUserId(1)
        print(shopcart[0].user_id)
        resp = self.app.get('/shopcarts/{}'.format(shopcart[0].user_id),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertTrue(len(resp.data) > 0)

        resp = self.app.get('/shopcarts/999',
                             content_type='application/json')
        #self.assertRaises(NotFound)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(resp.data)
        print(data)
        print(data['message'])
        self.assertIn('was not found', data['message'])
        ##self.assertEqual(len(json.loads(resp.data)),0)




         
    def test_list_all_shopcarts(self):
        """ Query all the shopcart in the system """
        shopcart = Shopcart.list_users()
        cnt = len(shopcart)
        print(cnt)
        print("----------------------------------------------------")
        resp = self.app.get('/shopcarts',
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)        
        print(resp.data); 
        data = json.loads(resp.data)
        self.assertEqual(cnt, len(data))

        Shopcart(user_id=30, product_id=1, quantity=5, price=12.00).save()
        Shopcart(user_id=31, product_id=2, quantity=5, price=12.00).save()
        shopcart = Shopcart.list_users()
        cnt = len(shopcart)
        resp = self.app.get('/shopcarts',
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)    
        data = json.loads(resp.data)
        self.assertEqual(cnt, len(data))



    def test_shop_cart_amount_by_user_id(self):
        """ Query the total amount of products in shopcart by user_id"""
        shopcarts = Shopcart.findByUserId(1)
        total = 0.0
        for shopcart in shopcarts:
             total = total + shopcart.price * shopcart.quantity
        total = round(total, 2)

        resp = self.app.get('/shopcarts/1/total',
                        content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(total, new_json['total_price'])

    def test_update_shopcart_quantity(self):

        """ Update a Shopcart quantity """
        # Add test product in database
        test_product = dict(user_id=1, product_id=1, quantity=5, price=12.00)
        data = json.dumps(test_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # make it chekc if the quantity is number
        shopcart = Shopcart.find(1,1)
        test_error = dict(user_id=1, product_id=1, quantity='a', price=12.00)
        data_error = json.dumps(test_error)
        resp = self.app.put('/shopcarts/{uid}/product/{pid}'.format(uid = shopcart.user_id, pid = shopcart.product_id),
                            data=data_error,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)




        # make it chekc if the quantity is more than 0
	shopcart = Shopcart.find(1,1)
	test_error = dict(user_id=1, product_id=1, quantity=0, price=12.00)
        data_error = json.dumps(test_error)
	resp = self.app.put('/shopcarts/{uid}/product/{pid}'.format(uid = shopcart.user_id, pid = shopcart.product_id),
                            data=data_error,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)



        # update the test product quantity
        shopcart = Shopcart.find(1, 1)
        resp = self.app.put('/shopcarts/{uid}/product/{pid}'.format(uid = shopcart.user_id, pid = shopcart.product_id),
                            data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


        #Check quantity is updated to 3
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['quantity'], 5)
   
        resp = self.app.put('/shopcarts/999/product/999',
                            data=data,
                            content_type='application/json')
        self.assertRaises(NotFound)

    def test_get_shopcart_product_info(self):
        """ Query quantity and price of a product shopcart by user_id and product_id """
        # Add test product in database
        test_product = dict(user_id=10, product_id=1, quantity=1, price=12.00)
        data = json.dumps(test_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Fetch info of product
        shopcart = Shopcart.find(10, 1)
        resp = self.app.get('/shopcarts/{}/product/{}'.format(shopcart.user_id, shopcart.product_id),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ans = json.loads(resp.data)
        self.assertEqual(ans['quantity'], shopcart.quantity)
        self.assertEqual(ans['price'], shopcart.price)

        resp = self.app.get('/shopcarts/999/product/999',
                            content_type='application/json')
        self.assertRaises(NotFound)



    def test_delete_product(self):
        """ Delete product in Shopcart """
        # Add test product in database
        test_product = dict(user_id=1, product_id=1, quantity=1, price=12.00)
        data = json.dumps(test_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Delet the test product
        shopcart = Shopcart.find(1, 1)
        resp = self.app.delete('/shopcarts/{uid}/product/{pid}'.format(uid = shopcart.user_id, pid = shopcart.product_id))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


    def test_get_users_by_total_cost_of_shopcart(self):
        Shopcart(user_id=3, product_id=1, quantity=5, price=12.00).save()
        resp = self.app.get('/shopcarts/users?amount=60',
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json.loads(resp.data)), 1)

    def test_get_users_by_total_cost_of_shopcart_bad_request(self):
        resp = self.app.get('/shopcarts/users?amount="hello"',
                            content_type='application/json')
        self.assertRaises(BadRequest)
        resp = self.app.get('/shopcarts/users',
                            content_type='application/json')
        self.assertRaises(NotFound)

    def test_delete_user_product(self):
        """ Delete products in Shopcart """
        # Add test products in database
        test_product = dict(user_id=1, product_id=1, quantity=1, price=12.00)
        data = json.dumps(test_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        test_product = dict(user_id=1, product_id=3, quantity=1, price=12.00)
        data = json.dumps(test_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Delet the test products of same user
        resp = self.app.delete('/shopcarts/{uid}'.format(uid = 1))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_reset(self):
        # Add test products in database
        test_product = dict(user_id=1, product_id=1, quantity=1, price=12.00)
        data = json.dumps(test_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        test_product = dict(user_id=1, product_id=3, quantity=1, price=12.00)
        data = json.dumps(test_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.app.delete('/shopcarts/reset')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_vcap_services(self):
        db_url = vcap.get_database_uri()
        self.assertNotEqual(db_url, "")

    def test_invalid_content_type(self):       
        data = dict(user_id=10, product_id=10, quantity=5, price=12.00)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='dict')
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


######################################################################
# Utility functions
######################################################################

    def get_product_count(self, user_id):
        """ save the current number of products in user's shopcart """
        resp = self.app.get('/shopcarts/'+str(user_id))
        #self.assertEqual(resp.status_code, status.HTTP_200_OK)
        if (resp.status_code == status.HTTP_404_NOT_FOUND):
		return 0
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
	data = json.loads(resp.data)
        return len(data)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()

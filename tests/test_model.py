"""
Test cases for Shopcart Model
Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import os
from app.model import Shopcart, DataValidationError, db
from app.service import app

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################

class TestShopcarts(unittest.TestCase):

    """ Test Cases for Shopcarts """

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
        Shopcart.init_db()
        db.drop_all()    # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_delete_a_product(self):
        """ Delete a Product """
        shopcart = Shopcart(user_id=1, product_id=1, quantity=1, price=12.00)
        shopcart.save()
        self.assertEqual(len(Shopcart.all()), 1)
        # delete item and make sure it isn't in the database
        shopcart.delete()
        self.assertEqual(len(Shopcart.all()), 0)

    def test_serialize_a_shopcart_entry(self):
        """ Test serialization of a Shopcart """
        shopcart = Shopcart(user_id = 1, product_id = 1, quantity = 1, price = 12.00)
        data = shopcart.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('user_id', data)
        self.assertEqual(data['user_id'], 1)
        self.assertIn('product_id', data)
        self.assertEqual(data['product_id'], 1)
        self.assertIn('quantity', data)
        self.assertEqual(data['quantity'], 1)
        self.assertIn('price', data)
        self.assertEqual(data['price'], 12.00)

    def test_deserialize_a_shopcart_entry(self):
        """ Test deserialization of a Shopcart """
        data = {"user_id": 1, "product_id": 1, "quantity": 1, "price": 12.00}
        shopcart = Shopcart()
        shopcart.deserialize(data)
        self.assertNotEqual(shopcart, None)
        self.assertEqual(shopcart.user_id, 1)
        self.assertEqual(shopcart.product_id, 1)
        self.assertEqual(shopcart.quantity, 1)
        self.assertEqual(shopcart.price, 12.00)
        self.test = 'test'
        self.assertRaises(DataValidationError)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, data)
        invalidKey = {"user_id": 1, "product_id": 1}
        self.assertRaises(DataValidationError, shopcart.deserialize, invalidKey)


    def test_find_shopcart_entry(self):
        """ Find a Shopcart by user_id and product_id """
        Shopcart(user_id=1, product_id=1, quantity=1, price=12.00).save()
        entry = Shopcart(user_id=1, product_id=2, quantity=1, price=15.00)
        entry.save()
        shopcart = Shopcart.find(entry.user_id, entry.product_id)
        self.assertIsNot(shopcart, None)
        self.assertEqual(shopcart.user_id, 1)
        self.assertEqual(shopcart.product_id, 2)
        self.assertEqual(shopcart.quantity, 1)
        self.assertEqual(shopcart.price, 15.00)


    def test_find_users_by_shopcart_amount(self):
        """Find users having goods worth more than specified amount in their shopcarts """
        Shopcart(user_id=1, product_id=1, quantity=1, price=12.00).save()
        Shopcart(user_id=1, product_id=2, quantity=1, price=12.00).save()
        Shopcart(user_id=2, product_id=1, quantity=1, price=12.00).save()

        result = Shopcart.find_users_by_shopcart_amount(13)
        self.assertEqual(result, [1])

    def test_create_a_shopcart_entry(self):
        """ Create a shopcart entry and assert that it exists """
        shopcart = Shopcart(user_id=999, product_id=999, quantity=999, price=999.99)
        self.assertTrue(shopcart != None)
        self.assertEqual(shopcart.user_id, 999)
        self.assertEqual(shopcart.product_id, 999)
        self.assertEqual(shopcart.quantity, 999)
        self.assertEqual(shopcart.price, 999.99)


    def test_add_a_shopcart_entry(self):
        """ Create a shopcart entry and add it to the database """
        shopcarts = Shopcart.findByUserId(999)
        before_cnt = (shopcarts.count())
        #self.assertEqual(shopcarts, [])
        shopcart = Shopcart(user_id=999, product_id=999, quantity=888, price=999.99)
        self.assertTrue(shopcarts != None)
        self.assertEqual(shopcart.user_id, 999)
        shopcart.save()
        # Asert that it was assigned an id and shows up in the database
        shopcarts2 = Shopcart.findByUserId(999)
        self.assertEqual(shopcarts2.count(), before_cnt+1)

    def test_update_a_shopcart_entry(self):
        """ Update a Shopcart entry """
        shopcart = Shopcart(user_id=999, product_id=999, quantity=999, price=999.99)
        shopcart.save()
        self.assertEqual(shopcart.user_id, 999)
        # Change it an save it
        shopcart.quantity =888
        shopcart.save()
        self.assertEqual(shopcart.user_id, 999)
        self.assertEqual(shopcart.product_id, 999)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        item = Shopcart.find(999,999)
        self.assertEqual(item.quantity, 888)


    def test_delete_a_shopcart_entry(self):
        """ Delete a shopcart entry """
        shopcart = Shopcart(user_id=999, product_id=999, quantity=999, price=999.99)
        shopcart.save()
        self.assertEqual(Shopcart.findByUserId(999).count(), 1)
        # delete item and make sure it isn't in the database
        shopcart.delete()
        self.assertEqual(Shopcart.findByUserId(999).count(), 0)


    def test_findByUserId(self):
        """ Find shopcart list by user_id """
        shopcart = Shopcart(user_id=999, product_id=999, quantity=999, price=999.99)
        shopcart.save()

        shopcarts = Shopcart.findByUserId(999)
        self.assertIsNot(shopcarts, None)
        self.assertEqual(shopcarts[0].user_id, shopcart.user_id)
        self.assertEqual(shopcarts[0].product_id, shopcart.product_id)



    def test_delete_user_product(self):
        """ Delete User Products """
        shopcart = Shopcart(user_id=1, product_id=1, quantity=1, price=12.00)
        shopcart.save()
        shopcart = Shopcart(user_id=1, product_id=2, quantity=1, price=12.00)
        shopcart.save()
        shopcart = Shopcart(user_id=1, product_id=3, quantity=1, price=12.00)
        shopcart.save()
        # delete item and make sure it isn't in the database
        shopcart.delete()
        shopcarts = Shopcart.findByUserId(1)
        self.assertIsNot(shopcarts, None)


    def test_remove_all(self):
        """ Remove all the shopcart data in the system """
        shopcart = Shopcart(user_id=1, product_id=1, quantity=1, price=12.00)
        shopcart.save()
        shopcart = Shopcart(user_id=1, product_id=2, quantity=1, price=12.00)
        shopcart.save()

        # delete data
        shopcart.remove_all()
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 0)



######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()

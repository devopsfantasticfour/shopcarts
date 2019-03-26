"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice
from app.models import DataValidationError, ShoppingCart, ShoppingCartItems

class ShoppingCartFactory(factory.Factory):
    """ Creates fake carts that you don't have to fill """
    class Meta:
        model = ShoppingCart
    userId = factory.Sequence(lambda n: n)
    state = FuzzyChoice(choices=['fill', 'activated', 'deactivated'])

class ShoppingCartItemsFactory(factory.Factory):
    """ Creates fake cart items that you don't have to add """
    class Meta:
        model = ShoppingCartItems
    productID = factory.fuzzy.FuzzyInteger(1, 142)
    price = factory.fuzzy.FuzzyFloat(1.99, 2999.99)
    quantity = FuzzyChoice(choices=[1, 3, 5, 8, 11, 2])
    cartId = FuzzyChoice(choices=[1, 2, 3, 4, 5, 6, 7, 8])

if __name__ == '__main__':
    for _ in range(50):
        shopcart = ShoppingCartFactory()
        print shopcart.serialize()
        shopcartitem = ShoppingCartItemsFactory()
        print(shopcartitem.serialize())

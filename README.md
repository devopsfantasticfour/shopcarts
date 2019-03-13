# shopcarts

The shopcarts resource allow customers to make a collection of products that they want to purchase. It should contain a reference to a product and the quantity the customer wants to buy. It may also contain the price of the product art the time they placed it in the cart. A customer will only have one shopcart. Since this is really a collection of product items, you will need to implement a subordinate API to place items into the shopcarts collection (e.g., /shopcarts/ {id}/items). You also will need to associate the shopcart with a customer preferably through it’s customer id.

Feature: The shopcarts store service back-end
  As a Shopcart Service Owner
  I need a RESTful catalog service
  So that I can keep track of all shopcarts

Background:
  Given data for shopcart entries
    | product_id | user_id | quantity | price |
    | 1          | 1       | 1        | 10.00 |
    | 2          | 1       | 1        | 15.00 |
    | 1          | 2       | 1        | 10.00 |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcarts REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: Add a new product
    When I visit the "Home Page"
    And I set the "Product Id" to 1
    And I set the "User Id" to 3
    And I set the "Quantity" to 1
    And I set the "Price" to 11.00
    And I press the "Create" button
    Then I should see the message "Success"

Scenario: Add a new product with invalid request
    When I visit the "Home Page"
    And I set the "Product Id" to 1
    And I set the "User Id" to 3
    And I set the "Quantity" to 0
    And I set the "Price" to 11.00
    And I press the "Create" button
    Then I should see the message "more than 0"


Scenario: Add same product
    When I visit the "Home Page"
    And I set the "Product Id" to 1
    And I set the "User Id" to 2
    And I set the "Quantity" to 1
    And I set the "Price" to 10.00
    And I press the "Create" button
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see 2 in the "Quantity" field

Scenario: Read information of a product from Shopcart of the user
  When I visit the "Home Page"
  And I set the "Product Id" to 1
  And I set the "User Id" to 2
  And I press the "Retrieve" button
  Then I should see the message "Success"
  And I should see 1 in the "Quantity" field
  And I should see 10.00 in the "Price" field


Scenario: Update information of a product from Shopcart of the user
    When I visit the "Home Page"
    And I set the "Product Id" to 1
    And I set the "User Id" to 2
    And I set the "Quantity" to 2
    And I set the "Price" to 13.00
    And I press the "Update" button
    And I press the "Clear" button
    And I set the "Product Id" to 1
    And I set the "User Id" to 2
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see 2 in the "Quantity" field
    And I should see 13.00 in the "Price" field

Scenario: Get user list having shopcart worth more than a given amount
    When I visit the "Home Page"
    And I set the "amount" to 15
    And I press the "Search" button
    Then I should see 1 in the query search results
    And I should not see 2 in the query search results
    


Scenario: Get list of products of a user's shopcart
    When I visit the "Home Page"
    And I set the "User Id" to 1
    And I press the "Retrieve-All" button
    Then I should see the message "Success"
    And I should see 2 in the results
    And I should not see 9 in the results

Scenario: Get total amount of user's shopcart
    When I visit the "Home Page"
    And I set the "User Id" to 1 
    And I press the "Total" button
    Then I should see the message "Success"
    And I should see 25 in the results
    And I should see 15 in the results


Scenario: Delete all the product from a user's shopcart
    When I visit the "Home Page"
    And I set the "User Id" to 1
    And I press the "Delete-All" button
    And I set the "User Id" to 1
    And I press the "Retrieve-All" button
    Then I should not see 2 in the results
    And I should not see 1 in the results

Scenario: Delete a product from a user's shopcart
    	    When I visit the "Home Page"
    	    And I set the "User Id" to 1
          And I set the "Product Id" to 2
    	    And I press the "Delete" button
    	    And I set the "User Id" to 1
    	    And I press the "Retrieve-All" button
    	    Then I should not see 2 in the results
          And I should see 1 in the results

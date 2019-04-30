"""
Shopcart Steps

Steps file for Shopcart.feature
"""
from os import getenv
import json
import requests
from behave import *
from compare import expect, ensure

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

WAIT_SECONDS=30

BASE_URL = getenv('BASE_URL', 'http://localhost:5000/')

@when('I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)

@then('I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)

@given('data for shopcart entries')
def step_impl(context):
    """ Delete all Shopcart entries and load new ones """
    headers = {'Content-Type': 'application/json'}
    context.resp = requests.delete(context.base_url + '/shopcarts/reset', headers=headers)
    expect(context.resp.status_code).to_equal(204)
    create_url = context.base_url + '/shopcarts'
    for row in context.table:
        data = {
            "product_id": row['product_id'],
            "user_id": row['user_id'],
            "quantity": row['quantity'],
            "price": row['price']
            }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)

@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@when('I set the "{element_name}" to {int_value}')
def step_impl(context, element_name, int_value):
    element_id = element_name.lower()
    element_id = element_id.replace(" ","_")
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(int_value)

@then('I should see the message "{message}"')
def step_impl(context, message):
    #element = context.driver.find_element_by_id('flash_message')
    #expect(element.text).to_contain(message)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
     )
    expect(found).to_be(True)

@then('I should see {int_value} in the "{element_name}" field')
def step_impl(context, int_value, element_name):
    element_id = element_name.lower()
    #element = context.driver.find_element_by_id(element_id)
    #expect(element.get_attribute('value')).to_equal(int_value)

    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
         expected_conditions.text_to_be_present_in_element_value(
             (By.ID, element_id),
             str(int_value)
         )
    )
    expect(found).to_be(True)



@then('I should see {value} in the results')
def step_impl(context, value):
    #element_id = context.driver.find_element_by_id('search_results')
    #expect(element.text).to_contain(value)

    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
         expected_conditions.text_to_be_present_in_element(
             (By.ID, 'search_results'),
             value
         )
    )
    expect(found).to_be(True)




@then('I should not see {value} in the results')
def step_impl(context, value):
    element = context.driver.find_element_by_id('search_results')
    #expect(element.text).to_contain(value)
    error_msg = "I should not see '%s' in '%s'" % (value, element.text)
    ensure(value in element.text, False, error_msg)




@then('I should see {value} in the query search results')
def step_impl(context, value):
    #element = context.driver.find_element_by_id('query_search_results')
    #expect(element.text).to_contain(value)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
         expected_conditions.text_to_be_present_in_element(
             (By.ID, 'query_search_results'),
             value
         )
    )
    expect(found).to_be(True)


@then('I should not see {value} in the query search results')
def step_impl(context, value):
    element = context.driver.find_element_by_id('query_search_results')
    error_msg = "I should not see '%s' in '%s' "%(value, element.text)
    ensure(value in element.text, False, error_msg)

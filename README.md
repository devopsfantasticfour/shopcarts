[![Build Status](https://travis-ci.org/devopsfantasticfour/shopcarts.svg?branch=master)](https://travis-ci.org/devopsfantasticfour/shopcarts)
[![codecov](https://codecov.io/gh/devopsfantasticfour/shopcarts/branch/master/graph/badge.svg)](https://codecov.io/gh/devopsfantasticfour/shopcarts)

# restful-flask-shopcart

This repo demonstrates **Test Driven Development** using `PyUnit` and `nose` (a.k.a. `nosetests`). It also demonstrates how to create a simple RESTful service using Python Flask and SQLite.

The resource model is persistences using SQLAlchemy to keep the application simple. It's purpose is to show the correct API calls and return codes that should be used for a REST API.

The shopcarts resource allow customers to make a collection of products that they want to purchase. It should contain a reference to a product and the quantity the customer wants to buy. It may also contain the price of the product art the time they placed it in the cart. A customer will only have one shopcart. Since this is really a collection of product items, you will need to implement a subordinate API to place items into the shopcarts collection (e.g., /shopcarts/ {id}/items). You also will need to associate the shopcart with a customer preferably through it’s customer id.

**Note:** The base service code is contained in `service.py` while the business logic for manipulating Pets is in the `models.py` file. This follows the popular Model View Controller (MVC) separation of duities by keeping the model separate from the controller. As such, we have two tests suites: one for the model (`test_model.py`) and one for the service itself (`test_service.py`)

## Prerequisite Installation using Vagrant

The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have this software the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Clone the project to your development folder and create your Vagrant vm

```sh
    git clone https://github.com/devopsfantasticfour/shopcarts.git
    cd shopcarts
    vagrant up
```

Once the VM is up you can use it with:

```sh
    vagrant ssh
    cd /vagrant
    python run.py
```

You should now be able to see the service running in your browser by going to
[http://localhost:5000](http://localhost:5000). You will see a message about the
service which looks something like this:

```
{
    name: "Shopping cart REST API Service",
    url: "http://localhost:5000/carts",
    version: "1.0"
}
```

When you are done, you can use `Ctrl+C` within the VM to stop the server.

## Alternative starting of the service

For running the service during development and debugging, you can also run the server
using the `flask` command with:

```sh
    flask run -h 0.0.0.0
```

Note that we need to bind the host IP address with `-h 0.0.0.0` so that the forwarded ports work correctly in **Vagrant**. If you were running this locally on your own computer you would not need this extra parameter.


## Testing

Run the tests suite with:

```sh
    nosetests
```

Nose is configured via the included `setup.cfg` file to automatically include the flags `--with-spec --spec-color` so that red-green-refactor is meaningful. If you are in a command shell that supports colors, passing tests will be green while failing tests will be red.

Nose is also configured to automatically run the `coverage` tool and you should see a percentage of coverage report at the end of your tests. If you want to see what lines of code were not tested use:

    $ coverage report -m

This is particularly useful because it reports the line numbers for the code that is not covered so that you can write more test cases to get higher code coverage.

You can also manually run `nosetests` with `coverage` (but `setup.cfg` does this already)

    $ nosetests --with-coverage --cover-package=app

Try and get as close to 100% coverage as you can.

It's also a good idea to make sure that your Python code follows the PEP8 standard. `flake8` has been included in the `requirements.txt` file so that you can check if your code is compliant like this:

    $ flake8 --count --max-complexity=10 --statistics model,service

I've also include `pylint` in the requirements. If you use a programmer's editor like Atom.io you can install plug-ins that will use `pylint` while you are editing. This catches a lot of errors while you code that would normally be caught at runtime. It's a good idea to always code with pylint active.

## Shutdown

When you are done, you can use the `exit` command to get out of the virtual machine just as if it were a remote server and shut down the vm with the following:

```sh
    exit
    vagrant halt
```

If the VM is no longer needed you can remove it with from your computer to free up disk space with:

```sh
    vagrant destroy
```

## What's featured in the project?

    * app/service.py -- the main Service using Python Flask
    * app/models.py -- the data model using SQLAlchemy
    * tests/test_service.py -- test cases against the service
    * tests/test_model.py -- test cases against the Shopcart and ShopcartItem model

This repo is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created by John Rofrano.

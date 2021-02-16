Stock simulation
=================
API
---

Create a user
~~~~~~~~~~~~~
The username will be unique and the key for using the
rest of the APIs.

.. sourcecode:: bash

  $ curl -v -L -X POST localhost:8000/user \
    --data '{"username": "sontek1", "first": "john", "last": "anderson", "budget":100000}'

Update a user
~~~~~~~~~~~~~
You can update all the information (first, last, budget) except
username.

.. sourcecode:: bash

  $ curl -v -L -X PATCH localhost:8000/user/sontek1 --data '{"first": "fred"}' 

Buy stocks
~~~~~~~~~~

.. sourcecode:: bash

  $ curl -v -L -X POST localhost:8000/stocks/sontek1/buy --data '{"date": "2017-1-3", "symbol": "AAPL", "quantity": 20}'

Sell stocks
~~~~~~~~~~~

.. sourcecode:: bash

  $ curl -v -L -X POST localhost:8000/stocks/sontek1/sell --data '{"date": "2017-1-3", "symbol": "AAPL", "quantity": 20}'

View value of portfolio
~~~~~~~~~~~~~~~~~~~~~~~
View portfolio based on a date:

.. sourcecode:: bash

  $ curl -v -L -X GET "localhost:8000/user/sontek1/portfolio?filter_date=2017-1-3"

Replacing the entire portfolio
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To override the entire portfolio you can upload a CSV

.. sourcecode:: bash

   $ curl -v -L -X PUT --form file='@replacement.csv' localhost:8000/user/sontek1/portfolio

This will replace the current portfolio.

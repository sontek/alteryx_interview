import mock
from pathlib import Path
from stocks.db import ORM

cwd = Path(__file__).parents[0]


def test_can_overwrite_portfolio(api_client):
    filename = (
        cwd / 'sample.csv'
    ).resolve()
    with open(filename, "rb") as f:
        response = api_client.put(
            "/user/sontek/portfolio",
            files={
                "file": (
                    "filename",
                    f,
                    "text/csv",
                )
            }
        )
    assert response.status_code == 200
    response = api_client.get(
        "/user/sontek/portfolio?filter_date=2017-2-1",
    )
    assert response.json() == {
        "success": True,
        "values": {
            'AAPL': '2540.20',
            'ADBE': '2817.02'
        }
    }


def test_can_create_user(api_client):
    response = api_client.post(
        "/user",
        json={
            "username": "sontek",
            "first": "John",
            "last": "Anderson",
            "budget": 100_000,
        }
    )
    assert response.json() == {
        'success': True,
        'user': {
            "username": "sontek",
            "first": "John",
            "last": "Anderson",
            "budget": 100_000,
        }
    }


def test_can_update(api_client):
    api_client.post(
        "/user",
        json={
            "username": "sontek",
            "first": "John",
            "last": "Anderson",
            "budget": 100_000,
        }
    )
    response = api_client.patch(
        "/user/sontek",
        json={
            "first": "Fred",
            "last": "Flintstone",
        }
    )
    assert response.json() == {
        'success': True,
        'user': {
            "username": "sontek",
            "first": "Fred",
            "last": "Flintstone",
            "budget": 100_000,
        }
    }


def test_can_buy_and_sell(api_client):
    api_client.post(
        "/user",
        json={
            "username": "sontek",
            "first": "John",
            "last": "Anderson",
            "budget": 100_000,
        }
    )

    response = api_client.post(
        "/stocks/sontek/buy",
        json={
            "date": "2017-12-27",
            "symbol": "WYNN",
            "quantity": 20,
        }
    )

    assert response.json() == {
        'success': True,
        "cost": 3325.2,
        "balance": 96674.8,
    }

    response = api_client.post(
        "/stocks/sontek/sell",
        json={
            "date": "2017-12-27",
            "symbol": "WYNN",
            "quantity": 20,
        }
    )

    assert response.json() == {
        "success": True,
        "value": 3325.2,
        "balance": 100_000.00,
    }


def test_sell_more_than_you_have(api_client):
    api_client.post(
        "/user",
        json={
            "username": "sontek",
            "first": "John",
            "last": "Anderson",
            "budget": 100_000,
        }
    )

    response = api_client.post(
        "/stocks/sontek/sell",
        json={
            "date": "2017-12-27",
            "symbol": "WYNN",
            "quantity": 20,
        }
    )

    assert response.json() == {
        'detail': "Can't sell more than you have"
    }


def test_cant_buy_more_than_budget(api_client):
    api_client.post(
        "/user",
        json={
            "username": "sontek",
            "first": "John",
            "last": "Anderson",
            "budget": 100_000,
        }
    )

    response = api_client.post(
        "/stocks/sontek/buy",
        json={
            "date": "2017-12-27",
            "symbol": "WYNN",
            "quantity": 100_000,
        }
    )

    assert response.json() == {
        'detail': "Can't spend more than you have"
    }


def test_can_get_value_of_portfolio(api_client):
    api_client.post(
        "/user",
        json={
            "username": "sontek",
            "first": "John",
            "last": "Anderson",
            "budget": 100_000,
        }
    )

    # Cost 3325.20
    api_client.post(
        "/stocks/sontek/buy",
        json={
            "date": "2017-12-27",
            "symbol": "WYNN",
            "quantity": 20,
        }
    )

    # Cost 2295.2
    api_client.post(
        "/stocks/sontek/buy",
        json={
            "date": "2017-1-3",
            "symbol": "AAPL",
            "quantity": 20,
        }
    )

    # Cost 2445.6
    api_client.post(
        "/stocks/sontek/buy",
        json={
            "date": "2017-6-26",
            "symbol": "ACN",
            "quantity": 20,
        }
    )

    # Value: 1222.80
    api_client.post(
        "/stocks/sontek/sell",
        json={
            "date": "2017-6-26",
            "symbol": "ACN",
            "quantity": 10,
        }
    )

    # Portfolio should be:
    # 93156.8

    response = api_client.get(
        "/user/sontek/portfolio?filter_date=2017-12-31",
    )

    assert response.json() == {
        "success": True,
        "values":  {
            'AAPL': '3384.40',
            'ACN': '1530.70',
            'WYNN': '3333.60'
        }
    }

    response = api_client.get(
        "/user/sontek/portfolio?filter_date=2017-1-3",
    )

    assert response.json() == {
        "success": True,
        "values":  {
            'AAPL': '2295.20',
        }
    }

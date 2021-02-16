import mock
import pytest
from tempfile import NamedTemporaryFile
from stocks.server import app, orm
from stocks.db import ORM
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def mock_orm():
    tempfile = NamedTemporaryFile(suffix='.db')

    new_orm = ORM(tempfile.name)
    new_orm.migrations()
    with mock.patch('stocks.server.orm', new=new_orm):
        yield


@pytest.fixture
def api_client():
    client = TestClient(app)
    return client

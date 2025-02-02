import pytest
import uuid

from app import create_app

class Helpers:
    @classmethod
    def generate_device_id(cls):
        return str(uuid.uuid4())

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True
    })
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def helpers():
    return Helpers

import pytest
import pytest_asyncio
from quart import Quart
import quart_babel as babel_ext

@pytest.fixture
def app():
    app = Quart(__name__)
    return app

@pytest.fixture
def babel(app):
    return babel_ext.Babel(app)
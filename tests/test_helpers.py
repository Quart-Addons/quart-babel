"""
Tests helper functions for getting the locale
and timezone from the request.
"""
import pytest
from quart import Quart

from quart_babel import select_locale_by_request, select_timezone_by_request

@pytest.mark.asyncio
async def test_select_locale_by_request():
    """
    Tests the select locale by request
    function.
    """
    app = Quart(__name__)

    header = {
        'accept-language': b'fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5'
    }

    async with app.test_request_context("/", headers=header):
        lang = select_locale_by_request()
        assert lang == 'fr-CH'

    header = {
        'accept-language': b'en-US,en;q=0.9,ru;q=0.8,ru-RU;q=0.7'
    }

    async with app.test_request_context("/", headers=header):
        lang = select_locale_by_request()
        assert lang == 'en-US'

@pytest.mark.asyncio
async def test_select_timezone_by_request():
    """
    Tests the select timezone by request
    function.
    """
    app = Quart(__name__)

    header = {'X-Real-IP': '72.28.33.80'}

    async with app.test_request_context("/", headers=header):
        timezone = select_timezone_by_request()
        assert timezone == 'America/New_York'

    header = {'X-Real-IP': '162.28.33.90'}

    async with app.test_request_context("/", headers=header):
        timezone = select_timezone_by_request()
        assert timezone == 'America/Los_Angeles'
    
"""
quart_babel.utils.async 

This module contains async helpers that
are useful for the Quart Babel Extension.
"""
import asyncio
from inspect import isasyncgenfunction, iscoroutinefunction
from typing import Callable, Coroutine

def _is_awaitable(func: Callable) -> bool:
    """
    Check than the given function is awaitable.
    This function was taken from `asgi-tools`,
    which can be found at https://github.com/klen/asgi-tools

    :param func: The function to check.
    :rtype: bool
    """
    return iscoroutinefunction(func) or isasyncgenfunction(func)

def _run_async(func: Coroutine):
    """
    Runs an async coroutine in a sync func.
    """
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(func)
    return result

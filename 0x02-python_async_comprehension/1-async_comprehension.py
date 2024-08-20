#!/usr/bin/env python3
""" 1-async_comprehension.py """
from typing import List

async_generator = __import__('0-async_generator').async_generator


async def async_comprehension() -> List[float]:
    """
    async_comprehension function
    """
    return [n async for n in async_generator()]

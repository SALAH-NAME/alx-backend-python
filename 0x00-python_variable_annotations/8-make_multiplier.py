#!/usr/bin/env python3
""" 8-make_multiplier.py """
from typing import Callable


def make_multiplier(multiplier: float) -> Callable[[float], float]:
    """
    make_multiplier function
    """

    def fn(num: float):
        return num * multiplier
    return fn

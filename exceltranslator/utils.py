# -*- coding: utf-8 -*-

"""Вспомогательные инструменты,
которые больше негде разместить из-за циклических импортов.
"""
import math
from functools import cached_property


def math_round(number: float, decimals: int = 0) -> float:
    """Округлить математическиим (не банковским) способом.

    Работает обычным математическим образом,
    в отличие от встроенной функции round(),
    которая использует банковское округление.

    >>> math_round(2.735, 2)
    2.74
    >>> round(2.735, 2)
    2.73
    """
    if number == float('inf') or number == float('-inf'):
        return number

    exp = number * 10 ** decimals
    if abs(exp) - abs(math.floor(exp)) < 0.5:
        return math.floor(exp) / 10 ** decimals
    return math.ceil(exp) / 10 ** decimals


class AsIsMixin:
    """Миксин для формирования коротких имён из докстригов.
    """

    @cached_property
    def short_name(self) -> str:
        """Динамически конструирует имя.
        """
        return self.__doc__.strip().rstrip('.')

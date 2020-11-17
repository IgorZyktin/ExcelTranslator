# -*- coding: utf-8 -*-

"""Базовые типы токенов.

Не подлежат регистрации т.к. не существуют сами по себе.
"""
import re
from typing import Callable, Optional, Tuple
from typing.re import Pattern

from exceltranslator.utils import AsIsMixin

__all__ = [
    'BaseToken',
    'LiteralToken',
    'NumberToken',
    'BinaryToken',
    'ConditionToken',
]


class BaseToken(AsIsMixin):
    """Базовый токен.
    """
    source_code: str = '' # как было
    base_pattern: str = ''  # как искать
    figure: str = ''  # как показывать
    flags: int = re.IGNORECASE | re.DOTALL  # параметры компиляции
    pattern: Pattern

    def __init__(self, source_code: str) -> None:
        """Инициализировать экземпляр.
        """
        self.source_code = source_code.strip()

    def __str__(self) -> str:
        """Вернуть текстовое представление.
        """
        return self.figure

    def __repr__(self) -> str:
        """Вернуть текстовое представление.
        """
        return type(self).__name__ + f'({self.source_code!r})'

    def __eq__(self, other) -> bool:
        """Проверка на равенство.
        """
        if type(self) == type(other) and self.figure == other.figure:
            return True
        return False

    @classmethod
    def try_making(cls, input_text: str)\
            -> Tuple[Optional['BaseToken'], Optional[int]]:
        """Попытаться создать экземпляр.
        """
        match = cls.pattern.match(input_text)
        if match:
            position = match.end()
            instance = cls(match.group())
            return instance, position
        return None, None


class LiteralToken(BaseToken):
    """Фактическое значение.
    """

    def __init__(self, source_code: str) -> None:
        """Инициализировать экземпляр.
        """
        super().__init__(source_code)
        self.figure = self.source_code


class NumberToken(LiteralToken):
    """Число.
    """


class BinaryToken(BaseToken):
    """Бинарный оператор.
    """
    _callable: Tuple[Callable]

    @property
    def callable(self):
        """Интерпретатор вызываемые объекты в теле класса методами.
        """
        return self._callable[0]


class ConditionToken(BaseToken):
    """Условие.
    """

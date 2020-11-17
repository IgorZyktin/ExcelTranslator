# -*- coding: utf-8 -*-

"""Типы данных лексического анализатора.
"""
import re
from operator import add, sub, mul, truediv, and_, or_, not_, le, lt, gt, ge
from typing import Type

from exceltranslator.exceptions import CustomSemanticError
from exceltranslator.lexer.base_tokens import (
    NumberToken, BaseToken, BinaryToken, LiteralToken, ConditionToken
)

__all__ = [
    'PowerToken',
    'IntegerToken',
    'LeftPar',
    'RightPar',
    'FloatToken',
    'StringToken',
    'NameToken',
    'Multiply',
    'Divide',
    'Minus',
    'Plus',
    'LT',
    'LE',
    'GT',
    'GE',
    'EqualToken',
    'NotEqualToken',
    'NotToken',
    'AndToken',
    'OrToken',
    'Semicolon',
    'Assignment',
    'CommaToken',
    'NullToken',
    'known_tokens',
    'LeftCur',
    'RightCur',
    'IfToken',
    'ElifToken',
    'ElseToken',
]

from exceltranslator.settings import EPSILON

known_tokens = []


def register(token_type: Type[BaseToken]) -> Type[BaseToken]:
    """Положи этот токен в список known_tokens.

    Добавляем игнорирование пробелов.
    """
    token_type.base_pattern = r'^\s*' + token_type.base_pattern
    token_type.pattern = re.compile(token_type.base_pattern,
                                    flags=token_type.flags)
    known_tokens.append(token_type)
    return token_type


def _delta(x, y):
    """Абсолютная разница между величинами.
    """
    return abs(x - y)


def good_eq(x, y):
    """Равно для float.
    """
    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
        return _delta(x, y) < EPSILON

    elif isinstance(x, str) and isinstance(y, str):
        return x == y

    raise CustomSemanticError(
        f'Можно проверять равенство только '
        f'строка-строка и число-число: {x!r} == {y!r}'
    )


def good_ne(x, y):
    """Не равно для float.
    """
    return not good_eq(x, y)


class NullToken(BaseToken):
    """Пустой токен.
    """
    base_pattern = r'(null)'

    def __init__(self) -> None:
        """Инициализировать экземпляр.
        """
        super().__init__('null')
        self.source_code = 'null'
        self.figure = 'null'


@register
class IntegerToken(NumberToken):
    """Целое число.
    """
    base_pattern = r'\b(?<!\.)(\d+)(?!\.)\b'


@register
class FloatToken(NumberToken):
    """Число с плавающей точкой.
    """
    base_pattern = r'\b(?<!\.)(\d+\.\d+)(?!\.)\b'


@register
class PowerToken(BinaryToken):
    """Степень.
    """
    base_pattern = r'(\*\*)'
    figure = '**'
    callable = pow


@register
class LeftPar(BaseToken):
    """Левая скобка.
    """
    base_pattern = r'(\()'
    figure = '('


@register
class RightPar(BaseToken):
    """Правая скобка.
    """
    base_pattern = r'(\))'
    figure = ')'


@register
class LeftCur(BaseToken):
    """Левая фигурная скобка.
    """
    base_pattern = r'(\{)'
    figure = '{'


@register
class RightCur(BaseToken):
    """Правая фигурная скобка.
    """
    base_pattern = r'(\})'
    figure = '}'


@register
class StringToken(LiteralToken):
    """Текстовое значение.
    """
    base_pattern = r'''(('|\").*?('|\"))'''


class NameToken(BaseToken):
    """Имя переменной или функции.
    """
    base_pattern = r'''(?!.?['\"])([a-zA-ZА-Яа-яёЁ][a-zA-ZА-Яа-я_ёЁ\d]*)'''

    def __init__(self, source_code: str) -> None:
        """Инициализировать экземпляр.
        """
        super().__init__(source_code)
        self.figure = self.source_code
        self.value = self.source_code


@register
class Multiply(BinaryToken):
    """Умножить.
    """
    base_pattern = r'(\*)(?!\*)'
    figure = '*'
    _callable = (mul,)


@register
class Divide(BinaryToken):
    """Разделить.
    """
    base_pattern = r'(\/)'
    figure = '/'
    _callable = (truediv,)


@register
class Plus(BinaryToken):
    """Плюс.
    """
    base_pattern = r'(\+)'
    figure = '+'
    _callable = (add,)


@register
class Minus(BinaryToken):
    """Минус.
    """
    base_pattern = r'(\-)'
    figure = '-'
    _callable = (sub,)


@register
class LT(BinaryToken):
    """Меньше.
    """
    base_pattern = r'(<)(?!\=)'
    figure = '<'
    _callable = (lt,)


@register
class GT(BinaryToken):
    """Больше.
    """
    base_pattern = r'(>)(?!\=)'
    figure = '>'
    _callable = (gt,)


@register
class LE(BinaryToken):
    """Меньше или равно.
    """
    base_pattern = r'(<=)'
    figure = '<='
    _callable = (le,)


@register
class GE(BinaryToken):
    """Больше или равно.
    """
    base_pattern = r'(>=)'
    figure = '>='
    _callable = (ge,)


@register
class EqualToken(BinaryToken):
    """Равно.
    """
    base_pattern = r'(==)'
    figure = '=='
    _callable = (good_eq,)


@register
class NotEqualToken(BinaryToken):
    """Не равно.
    """
    base_pattern = r'(!=)'
    figure = '!='
    _callable = (good_ne,)


@register
class AndToken(BinaryToken):
    """Логическое И.
    """
    base_pattern = r'(И|AND)\s'
    _callable = (and_,)
    figure = 'and'


@register
class OrToken(BinaryToken):
    """Логическое ИЛИ.
    """
    base_pattern = r'(ИЛИ|OR)\s'
    _callable = (or_,)
    figure = 'or'


@register
class NotToken(BinaryToken):
    """Логическое НЕ.
    """
    base_pattern = r'(НЕ|NOT)\s'
    _callable = (not_,)
    figure = 'not'


@register
class Assignment(BaseToken):
    """Присваивание.
    """
    base_pattern = r'(=)(?!=)'
    figure = '='


@register
class Semicolon(BaseToken):
    """Точка с запятой.
    """
    base_pattern = r'(;)'
    figure = ';'


@register
class CommaToken(BaseToken):
    """Запятая.
    """
    base_pattern = r'(,)'
    figure = ','


@register
class IfToken(ConditionToken):
    """Условие (голова).
    """
    base_pattern = r'(ЕСЛИ|IF)'
    figure = 'if'


@register
class ElifToken(ConditionToken):
    """Условие (продолжение).
    """
    base_pattern = r'(ИНАЧЕ_ЕСЛИ|ELIF)'
    figure = 'elif'


@register
class ElseToken(ConditionToken):
    """Условие (хвост).
    """
    base_pattern = r'(ИНАЧЕ|ELSE)'
    figure = 'else'


# чтобы не было конфликтов с зарезервированными
# словами, имя идёт последним в списке
NameToken = register(NameToken)

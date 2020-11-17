# -*- coding: utf-8 -*-

"""Собственные исключения проекта.
"""


class CustomException(Exception):
    """Базовое исключение.
    """


class CustomSyntaxError(CustomException):
    """Ошибка синтаксиса внутри компилируемого кода.
    """


class CustomSemanticError(CustomException):
    """Ошибка семантики внутри компилируемого кода.
    """

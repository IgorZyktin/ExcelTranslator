# -*- coding: utf-8 -*-

"""Перечень стандартных функций.
"""
import math
import random
from functools import lru_cache
from operator import mod
from typing import Callable

from exceltranslator.utils import math_round


def custom_sum(*args):
    """Замена стандартной sum.

    Чтобы пользователи могли суммировать не только iterable.
    """
    return sum(args)


def custom_avg(*args) -> float:
    """Вычисление среднего.
    """
    return sum(args) / len(args)


def custom_concatenate(*args) -> str:
    """Конкатенация объектов.
    """
    return ''.join(map(str, args))


def custom_join(*args) -> str:
    """Конкатенация объектов с разделителем.
    """
    if not args:
        return ""

    elif len(args) == 1:
        return str(args[0])

    return str(args[0]).join(map(str, args))


def custom_all(*args) -> bool:
    """Аналог all.
    """
    return bool(all(args) and args)


def custom_any(*args) -> bool:
    """Аналог any.
    """
    return bool(any(args) and args)


def custom_not_any(*args) -> bool:
    """Аналог not any.
    """
    return not custom_any(*args)


SCRIPT_NAME_TO_PYTHON_NAME = {
    # now
    'реальное время': 'realtime',

    # today
    'название дня': 'day_name',
    'номер дня': 'day_number',
    'число': 'day',
}

DEFAULT_FUNCTIONS = {
    # математические
    'СЛЧИС': random.random,
    'МИН': min,
    'МАКС': max,
    'СУММ': custom_sum,
    'ABS': abs,
    'ОКРУГЛ': math_round,
    'ОКРВВЕРХ': math.ceil,
    'ОКРВНИЗ': math.floor,
    'ЦЕЛОЕ': int,
    'ОСТАТ': mod,
    'СЛУЧМЕЖДУ': random.randint,
    'КОРЕНЬ': math.sqrt,
    'ОТБР': math.trunc,
    'СРЗНАЧ': custom_avg,

    # текстовые
    'ТЕКСТ': str,
    'ЗНАЧЕН': float,
    'СТРОЧН': str.lower,
    'ПРОПИСН': str.upper,
    'СЦЕПИТЬ': custom_concatenate,
    'ОБЪЕДИНИТЬ': custom_join,

    # логические
    'ВСЕ_ИЗ': custom_all,
    'ОДИН_ИЗ': custom_any,
    'НИ_ОДИН_ИЗ': custom_not_any,

    # дата и время

    # специальные
    'ТОЧКА': lambda *_: 0,  # заглушка, реальный код в другом пакете
    'СЕЙЧАС': lambda *_: 0,  # заглушка, реальный код в другом пакете
    'СЕГОДНЯ': lambda *_: 0,  # заглушка, реальный код в другом пакете
    'MQTT': lambda *_: 0,  # заглушка, реальный код в другом пакете
    'ОТЧЁТ': lambda *_: 0,  # заглушка, реальный код в другом пакете
    'СОХР': lambda *_: 0,  # заглушка, реальный код в другом пакете
    'ЗАГР': lambda *_: 0,  # заглушка, реальный код в другом пакете
}

DEFAULT_NAMES = {
    'ЛОЖЬ': 0,
    'ИСТИНА': 1,
}


class FuncWrapper:
    """Обёртка для функций, чтобы не было видно, что они стандартные.
    """

    def __init__(self, func: Callable, repr_: str):
        """Инициализировать экземпляр.
        """
        self.func = func
        self.repr = repr_

    def __call__(self, *args, **kwargs):
        """Вызвать настоящую функцию.
        """
        return self.func(*args, **kwargs)

    def __repr__(self):
        """Вернуть текстовое представление.
        """
        return self.repr


def translate_script_name(original_name: str) -> str:
    found = SCRIPT_NAME_TO_PYTHON_NAME.get(original_name)
    if found is None:
        found = f'?{original_name}?'
    return found


@lru_cache
def get_default_functions() -> dict:
    """Получить все готовые функции.

    Сюда можно добавить обработку всех функций разом.
    """
    output = {}
    for name, contents in DEFAULT_FUNCTIONS.items():
        output[name] = FuncWrapper(contents, f'<функция {name}>')
    return output


def get_default_names() -> dict:
    """Получить все готовые имена.
    """
    return {**get_default_functions(), **DEFAULT_NAMES}


def non_standard(resulting_dict: dict) -> dict:
    """Выделить из словаря нестандартные имена.
    """
    return {
        key: value
        for key, value in resulting_dict.items()
        if key not in DEFAULT_FUNCTIONS
    }

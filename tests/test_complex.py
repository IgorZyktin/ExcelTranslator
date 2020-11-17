# -*- coding: utf-8 -*-

"""Тесты сложных операций.
"""
from random import random

import pytest

from exceltranslator import exceptions
from exceltranslator.helpers.namespace_wrapper import (
    NamespaceWrapper,
    Namespace,
)
from exceltranslator.tools import custom_eval


def test_assignment():
    source_code = """
    x = 1;
    """
    namespace = NamespaceWrapper()
    res = custom_eval(source_code, namespace)
    assert res is None
    assert namespace.dict() == {'x': 1}

    source_code = """
    x = "test"
    """
    with pytest.raises(exceptions.CustomSemanticError,
                       match='Попытка изменения типа'):
        custom_eval(source_code, namespace)


def test_instructions():
    source_code = """
    x = 1;
    y = 2;
    z = x + y;
    """
    namespace = NamespaceWrapper()
    res = custom_eval(source_code, namespace)
    assert res is None
    assert namespace.dict() == {'x': 1, 'y': 2, 'z': 3}


@pytest.mark.parametrize('source_code', [
    ''' 'test' == "test" ''',
    ''' 0.1 + 0.1 + 0.1 == 0.3 ''',
])
def test_equality(source_code):
    assert custom_eval(source_code)


def test_conditions():
    for _ in range(22):
        source_code = """
        num = СЛЧИС() * 10;
        ЕСЛИ (num >= 9)
        {
            x = ">= 9";
        }
        ИНАЧЕ_ЕСЛИ (num >= 8) 
        {
            x = ">= 8";
        } 
        ИНАЧЕ_ЕСЛИ (num >= 7) 
        {
            x = ">= 7";
        } 
        ИНАЧЕ_ЕСЛИ (num >= 6) 
        {
            x = ">= 6";
        } 
        ИНАЧЕ_ЕСЛИ (num >= 5) 
        {
            x = ">= 5";
        } 
        ИНАЧЕ_ЕСЛИ (num >= 4) 
        {
            x = ">= 4";
        } 
        ИНАЧЕ_ЕСЛИ (num >= 3) 
        {
            x = ">= 3";
        } 
        ИНАЧЕ_ЕСЛИ (num >= 2) 
        {
            x = ">= 2";
        } 
        ИНАЧЕ 
        {
            x = "около 1";
        };
        """
        namespace = NamespaceWrapper(dict(СЛЧИС=random))
        custom_eval(source_code, namespace)
        x = namespace['x']
        num = int(namespace['num'])

        if num <= 1:
            assert x == 'около 1'

        else:
            assert x == f'>= {num}'


def test_abs():
    for _ in range(22):
        source_code = """
        num = СЛЧИС() * 2;
        ЕСЛИ (ABS(num - 2) < 0.1)
        {
            x = "примерно два";
        }
        ИНАЧЕ
        {
            x = "не два";
        } 
        """
        namespace = Namespace()
        custom_eval(source_code, namespace)
        x = namespace['x']

        if abs(namespace['num'] - 2) < 0.1:
            assert x == 'примерно два', namespace['num']

        else:
            assert x == 'не два', namespace['num']

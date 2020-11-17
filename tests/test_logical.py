# -*- coding: utf-8 -*-

"""Тесты сложных операций.
"""
import pytest

from exceltranslator.helpers.namespace_wrapper import NamespaceWrapper
from exceltranslator.tools import custom_eval


@pytest.mark.parametrize('text_in', [
    '1 > 2',
    '2 >= 4',
    '3 + 1 < 6 - 9',
    '2 > 18',
    '6 <= 2',
    '9 != 9',
    '9 != 9.0',
    '2 == 2 and 0 > 5',
    '0 or 0',
])
def test_false(text_in):
    res = custom_eval(text_in)
    assert not res


@pytest.mark.parametrize('text_in', [
    '1 < 2',
    '2 <= 4',
    '3 + 1 > 6 - 9',
    '2 < 18',
    '6 >= 2',
    '9 == 9',
    '9 == 9.0',
    '2 == 2 or 0 > 5',
    '1 and 1',
    'not 0',
    'not 0.0',
    '3 * 0.1 == 0.1 + 0.1 + 0.1',
    '0.1 == (0.1 + 0.1 + 0.1) / 3',
])
def test_true(text_in):
    res = custom_eval(text_in)
    assert res


@pytest.mark.parametrize('text_in, ref', [
    ('if(x==0){x=25}', 25),
    ('if(x>1){x=91}', 0),
    ('if(x!=1){x=55};if(x==55){x=18};', 18),
    ('if(x==1){x=100}else{x=55}', 55),
    ('if(x==0){x=100}else{x=55}', 100),
    ('if(x>=1){x=100}elif(x==0){x=17}else{x=55}', 17),
])
def test_if(text_in, ref):
    namespace = NamespaceWrapper({'x': 0})
    custom_eval(text_in, namespace)
    assert namespace['x'] == ref

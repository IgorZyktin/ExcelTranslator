# -*- coding: utf-8 -*-

"""Тесты лексического анализатора.
"""
import pytest

from exceltranslator.exceptions import CustomSyntaxError
from exceltranslator.lexer.lexer import Lexer


@pytest.fixture()
def instance():
    inst = Lexer()
    return inst


@pytest.mark.parametrize('text_in', [
    '',
    '""',
    '""""',
    '""""""',
    '""""""""""""""""""""""((()))""""""""""""""""""""""',
    ''' '""' ''',
    ''' "" '' "" ''',
    "''",
    "''''",
    "''''''''",
    "'''''''''''''''''''''''''{{{{(((((()()()())))))}}}}'''''''''''''''''''''''''",
    "''""''",
])
def test_incorrect_quotes_good(instance, text_in):
    assert not instance.check_quotes(text_in)


@pytest.mark.parametrize('text_in', [
    '''"''',
    """'""",
    '''"""''',
    '''""'''""'"''',
])
def test_incorrect_quotes_bad(instance, text_in):
    with pytest.raises(CustomSyntaxError):
        instance.check_quotes(text_in)


@pytest.mark.parametrize('text_in', [
    '',
    '[]',
    '{}',
    '()',
    '((()))',
    '()()',
    '[][]',
    '{}{}',
    '([(())])',
    '{{((()))}}',
    '{{{{(((((()()()())))))}}}}',
    '([(){}]{()(){}}[]{}{}()())',
])
def test_incorrect_parenthesis_good(instance, text_in):
    assert not instance.check_parenthesis(text_in)


def syntax_error(index: int):
    array = [
        'Синтаксическая ошибка: символ "]" (№3) не имеет пары. [( --> ] <-- )',
        'Синтаксическая ошибка: символ "[" (№1) не имеет пары.  --> [ <-- ',
        'Синтаксическая ошибка: символ "]" (№1) не имеет пары.  --> ] <-- ',
        'Синтаксическая ошибка: символ "(" (№1) не имеет пары.  --> ( <-- ',
        'Синтаксическая ошибка: символ ")" (№1) не имеет пары.  --> ) <-- ',
        'Синтаксическая ошибка: символ "{" (№1) не имеет пары.  --> { <-- ',
        'Синтаксическая ошибка: символ "}" (№1) не имеет пары.  --> } <-- ',
        'Синтаксическая ошибка: символ "{" (№3) не имеет пары. {} --> { <-- ',
        'Синтаксическая ошибка: символ "]" (№6) не имеет пары. ([]{} --> ] <-- )',
        'Синтаксическая ошибка: символ "(" (№3) не имеет пары. (( --> ( <-- ',
        'Синтаксическая ошибка: символ "}" (№1) не имеет пары.  --> } <-- }}',
        'Синтаксическая ошибка: символ "}" (№4) не имеет пары. {}[ --> } <-- ]',
        'Синтаксическая ошибка: символ ")" (№46) не имеет пары. ...) - 8 * 8) --> ) <-- )))',
        'Синтаксическая ошибка: символ ")" (№4) не имеет пары. +60 --> ) <-- *82)-82*(...',
    ]
    return array[index]


@pytest.mark.parametrize('text_in,index', [
    ('[(])', 0),
    ('[', 1),
    (']', 2),
    ('(', 3),
    (')', 4),
    ('{', 5),
    ('}', 6),
    ('{}{', 7),
    ('([]{}])', 8),
    ('(((', 9),
    ('}}}', 10),
    ('{}[}]', 11),
    ('1 * (2 + (4 * (9 + (4 + 2) * 3) + 9) - 8 * 8)))))', 12),
    ('+60)*82)-82*(32+79-(88)*33)+15)+40)+57*(53)', 13),
])
def test_incorrect_parenthesis_bad(instance, text_in, index):
    with pytest.raises(CustomSyntaxError) as error:
        instance.check_parenthesis(text_in)
    assert error.value.args[0] == syntax_error(index)

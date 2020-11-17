# -*- coding: utf-8 -*-

"""Тесты лексического анализатора.
"""
import pytest

from exceltranslator.lexer.lexer import Lexer
from exceltranslator.lexer.tokens import *


@pytest.fixture()
def instance():
    inst = Lexer()
    return inst


@pytest.mark.parametrize('token_type,text_left,text_right', [
    (PowerToken, '**', '  **   '),
    (IntegerToken, '456', ' 456 '),
    (LeftPar, ' (', '('),
    (RightPar, ')', ')  '),
    (FloatToken, '2.56', '2.56'),
    (StringToken, '"test"', '"test"'),
    (NameToken, 'x', '  x '),
    (Multiply, '*', '*'),
    (Divide, '/', '  /'),
    (Minus, '-', '  -'),
    (Plus, '+', '  + '),
    (LT, '<', '  <'),
    (LE, '<=', '  <= '),
    (GT, '>', ' > '),
    (GE, '>=', ' >=  '),
    (EqualToken, '==', '  ==  '),
    (NotToken, 'NOT', '  NOT  '),
    (AndToken, 'AND', ' AND '),
    (OrToken, 'OR', ' OR '),
    (Semicolon, '; ', '; '),
    (Assignment, ' =  ', '='),
    (CommaToken, ',', '  , '),
    (IfToken, 'ЕСЛИ', '  ЕСЛИ '),
    (ElifToken, 'ИНАЧЕ_ЕСЛИ', '  ИНАЧЕ_ЕСЛИ '),
    (ElseToken, 'ИНАЧЕ', '  ИНАЧЕ '),
])
def test_creation(token_type, text_left, text_right):
    reference = token_type(text_left)
    result = token_type(text_right)
    assert reference is not None
    assert reference == result


@pytest.mark.parametrize('text_in,tokens_out', [
    ('x = 1', [NameToken('x'), Assignment('='), IntegerToken('1')]),
    ('x = 2.15', [NameToken('x'), Assignment('='), FloatToken('2.15')]),
    ('x = "test"', [NameToken('x'), Assignment('='), StringToken('"test"')]),
    ('2 * 5', [IntegerToken("2"), Multiply("*"), IntegerToken("5")]),
    ('2 * 5**6',
     [IntegerToken("2"), Multiply("*"), IntegerToken("5"), PowerToken("**"),
      IntegerToken("6")]),
    ('3 + 4 * 1',
     [IntegerToken("3"), Plus("+"), IntegerToken("4"), Multiply("*"),
      IntegerToken("1")]),
    ('8;4', [IntegerToken("8"), Semicolon(";"), IntegerToken("4")]),
    ('x == y', [NameToken("x"), EqualToken("=="), NameToken("y")]),
    ('a = x AND y OR z',
     [NameToken("a"), Assignment("="), NameToken("x"), AndToken("AND"),
      NameToken("y"), OrToken("OR"), NameToken("z")]),
    ('u, n, m',
     [NameToken("u"), CommaToken(","), NameToken("n"), CommaToken(","),
      NameToken("m")]),
    ('>= > <= <', [GE(">="), GT(">"), LE("<="), LT("<")]),
    ('10 / p', [IntegerToken("10"), Divide("/"), NameToken("p")]),

])
def test_tokenize(instance, text_in, tokens_out):
    assert instance.tokenize(text_in) == tokens_out


@pytest.mark.parametrize('token_type,variants', [
    (IntegerToken, ["1", "   2", "\n3", "\t4"]),
    (FloatToken, ["1.25", "   2.14", "\n3.05", "\t4.0"]),
    (StringToken, ["'1'", "   '2.14'", '"\n3.05"', "\t'4.0'"]),
])
def test_recognition(token_type, variants):
    for variant in variants:
        token, end = token_type.try_making(variant)
        assert type(token) == token_type, variant

# -*- coding: utf-8 -*-

"""Тесты вложенных конструкций.
"""
import pytest

from exceltranslator.lexer.lexer import Lexer
from exceltranslator.parser.parser import Parser
from exceltranslator.parser.serialization import (
    serialize_to_text, serialize_to_python,
)

SOURCE_1 = "ЕСЛИ(x>(x+(1*4**3))){x=1;f=ABS(-5);}" \
           "ИНАЧЕ_ЕСЛИ(25+(86+71*(23-23))){y=1;f=ABS(-5);}" \
           "ИНАЧЕ{z=1;f=ABS(-5);};x=25;"

SOURCE_2 = """
ЕСЛИ(1)
{
    ЕСЛИ(2)
    {
        ЕСЛИ(3)
        {
            x = 1
            x = 1
            x = 1
        }
        ИНАЧЕ
        {
            ЕСЛИ(0) 
            {
                y = 999
                y = 999
                y = 999
            }
            x = 2
            x = 2
            x = 2
        }
    }
    ИНАЧЕ
    {
        x = 3
        x = 3
        x = 3
    }
}
ИНАЧЕ
{
    x = 4
    x = 4
    x = 4
}
"""

REF_TEXT_2 = """
ЕСЛИ (1)
{
    ЕСЛИ (2)
    {
        ЕСЛИ (3)
        {
            x = 1;
            x = 1;
            x = 1;
        }
        ИНАЧЕ
        {
            ЕСЛИ (0)
            {
                y = 999;
                y = 999;
                y = 999;
            };
            x = 2;
            x = 2;
            x = 2;
        };
    }
    ИНАЧЕ
    {
        x = 3;
        x = 3;
        x = 3;
    };
}
ИНАЧЕ
{
    x = 4;
    x = 4;
    x = 4;
};
""".strip()

REF_TEXT_1 = """
ЕСЛИ (x > (x + (1 * 4 ** 3)))
{
    x = 1;
    f = ABS(-5);
}
ИНАЧЕ_ЕСЛИ (25 + (86 + 71 * (23 - 23)))
{
    y = 1;
    f = ABS(-5);
}
ИНАЧЕ
{
    z = 1;
    f = ABS(-5);
};
x = 25;
""".strip()

REF_PYTHON_1 = """
if x > (x + (1 * 4 ** 3)):
    x = 1
    f = abs(-5)

elif 25 + (86 + 71 * (23 - 23)):
    y = 1
    f = abs(-5)

else:
    z = 1
    f = abs(-5)

x = 25
""".strip()

REF_PYTHON_2 = """
if 1:
    if 2:
        if 3:
            x = 1
            x = 1
            x = 1

        else:
            if 0:
                y = 999
                y = 999
                y = 999
            x = 2
            x = 2
            x = 2


    else:
        x = 3
        x = 3
        x = 3


else:
    x = 4
    x = 4
    x = 4
""".strip()


@pytest.mark.parametrize('source, ref_text', [
    (SOURCE_1, REF_TEXT_1),
    (SOURCE_2, REF_TEXT_2),
])
def test_text(source, ref_text):
    lexer = Lexer()
    parser = Parser(lexer)
    lexer.analyze(source)
    root = parser.parse()
    assert serialize_to_text(root) == ref_text


@pytest.mark.parametrize('source, ref_text', [
    (SOURCE_1, REF_PYTHON_1),
    (SOURCE_2, REF_PYTHON_2),
])
def test_python(source, ref_text):
    lexer = Lexer()
    parser = Parser(lexer)
    lexer.analyze(source)
    root = parser.parse()
    assert serialize_to_python(root) == ref_text

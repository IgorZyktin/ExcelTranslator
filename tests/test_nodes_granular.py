# -*- coding: utf-8 -*-

"""Тесты нод по кусочку.
"""
import pytest

from exceltranslator import exceptions
from exceltranslator.helpers.namespace_wrapper import NamespaceWrapper
from exceltranslator.helpers.stack_wrapper import StackWrapper
from exceltranslator.lexer.tokens import *
from exceltranslator.parser.base_nodes import *
from exceltranslator.parser.nodes import *
from exceltranslator.parser.serialization import (
    serialize_to_text, serialize_to_python,
)

CONDITION_TEXTUAL_1 = """
ЕСЛИ (14.0 >= 14.0)
{
    x = "test";
}
ИНАЧЕ_ЕСЛИ (14.0 and 14.0)
{
    x = "not actually test";
}
ИНАЧЕ
{
    x = "really not test";
};""".strip()

CONDITION_TEXTUAL_2 = """
ЕСЛИ (1.0 >= 14.0)
{
    x = "test";
}
ИНАЧЕ_ЕСЛИ (1.0 and 14.0)
{
    x = "not actually test";
}
ИНАЧЕ
{
    x = "really not test";
};""".strip()

CONDITION_TEXTUAL_3 = """
ЕСЛИ (0.0 >= 14.0)
{
    x = "test";
}
ИНАЧЕ_ЕСЛИ (0.0 and 14.0)
{
    x = "not actually test";
}
ИНАЧЕ
{
    x = "really not test";
};""".strip()

CONDITION_PYTHONIC_1 = '''
if math_round(14.0, 5) >= math_round(14.0, 5):
    x = "test"

elif math_round(14.0, 5) and math_round(14.0, 5):
    x = "not actually test"

else:
    x = "really not test"
'''.strip()

CONDITION_PYTHONIC_2 = """
if math_round(1.0, 5) >= math_round(14.0, 5):
    x = "test"

elif math_round(1.0, 5) and math_round(14.0, 5):
    x = "not actually test"

else:
    x = "really not test"
""".strip()

CONDITION_PYTHONIC_3 = """
if math_round(0.0, 5) >= math_round(14.0, 5):
    x = "test"

elif math_round(0.0, 5) and math_round(14.0, 5):
    x = "not actually test"

else:
    x = "really not test"
""".strip()


def test_variable_string():
    node = VarNode(StringToken('"123"'))
    assert str(node) == 'VarNode (value="123")'
    assert repr(node) == 'VarNode (value="123")'
    assert node.short_name == '"123"'

    stack = StackWrapper()
    node.eval(NamespaceWrapper(), stack)
    assert stack.pop(node) == '123'

    assert serialize_to_text(node) == '"123"'
    assert serialize_to_python(node) == '"123"'


def test_variable_int():
    node = VarNode(IntegerToken('123'))
    assert str(node) == 'VarNode (value=123)'
    assert repr(node) == 'VarNode (value=123)'
    assert node.short_name == '123'

    stack = StackWrapper()
    node.eval(NamespaceWrapper(), stack)
    assert stack.pop(node) == 123.0

    assert serialize_to_text(node) == '123'
    assert serialize_to_python(node) == '123'


def test_variable_float():
    node = VarNode(FloatToken('123.031213120121'))
    assert str(node) == 'VarNode (value=123.031213120121)'
    assert repr(node) == 'VarNode (value=123.031213120121)'
    assert node.short_name == '123.031213120121'

    stack = StackWrapper()
    node.eval(NamespaceWrapper(), stack)
    assert stack.pop(node) == 123.03121

    assert serialize_to_text(node) == '123.031213120121'
    assert serialize_to_python(node) == 'math_round(123.031213120121, 5)'


def test_variable_bad():
    node = VarNode(NotToken(''))
    with pytest.raises(exceptions.CustomSemanticError,
                       match='Неизвестный тип переменной: not.*'):
        node.eval(NamespaceWrapper(), StackWrapper())


def test_unary_minus():
    node = UnaryMinusNode(VarNode(IntegerToken('123')))
    assert str(node) == 'UnaryMinusNode'
    stack = StackWrapper()
    node.eval(NamespaceWrapper(), stack)
    assert stack.pop(node) == -123.0

    node = UnaryMinusNode(VarNode(FloatToken('123.031213120121')))
    node.eval(NamespaceWrapper(), stack)
    assert stack.pop(node) == -123.03122

    assert serialize_to_text(node) == '-123.031213120121'
    assert serialize_to_python(node) == 'math_round(-123.031213120121, 5)'


def test_name():
    node = NameNode(NameToken('test'))
    assert str(node) == 'NameNode (value="test")'
    stack = StackWrapper()
    node.eval(NamespaceWrapper({'test': 1}), stack)
    assert stack.pop(node) == 1

    assert node.short_name == 'Имя(test)'

    with pytest.raises(exceptions.CustomSemanticError,
                       match='Переменная с именем "test" не найдена.'):
        node.eval(NamespaceWrapper(), stack)

    assert serialize_to_text(node) == 'test'
    assert serialize_to_python(node) == 'test'


def test_binary_node():
    node = BinaryNode(
        left_operand=VarNode(FloatToken('1.75')),
        operator=Divide('/'),
        right_operand=VarNode(FloatToken('2.34')),
    )
    node_div = BinaryNode(
        left_operand=VarNode(FloatToken('1.75')),
        operator=Divide('/'),
        right_operand=VarNode(FloatToken('0.0')),
    )
    node_mixed = BinaryNode(
        left_operand=VarNode(StringToken('1.75')),
        operator=Divide('/'),
        right_operand=VarNode(FloatToken('0.1')),
    )
    assert str(node) == 'BinaryNode (Divide)'
    stack = StackWrapper()
    node.eval(NamespaceWrapper(), stack)
    assert stack.pop(node) == 0.74786

    node_div.eval(NamespaceWrapper(), stack)
    assert stack.pop(node) == float('inf')

    assert node.short_name == 'Разделить'

    with pytest.raises(exceptions.CustomSemanticError,
                       match="Нельзя осуществлять операцию '1.75' / 0.1"):
        node_mixed.eval(NamespaceWrapper(), stack)

    assert serialize_to_text(node) == '1.75 / 2.34'
    assert serialize_to_python(node) == 'math_round(1.75, 5) / ' \
                                        'math_round(2.34, 5)'


def test_logical_node():
    node_and = LogicalNode(
        left_operand=VarNode(FloatToken('1.75')),
        operator=AndToken('И'),
        right_operand=VarNode(FloatToken('2.34')),
    )
    node_or = LogicalNode(
        left_operand=VarNode(FloatToken('0.0')),
        operator=OrToken('ИЛИ'),
        right_operand=VarNode(FloatToken('0.1')),
    )
    node_and_false = LogicalNode(
        left_operand=VarNode(FloatToken('0.0')),
        operator=AndToken('И'),
        right_operand=VarNode(FloatToken('1.0')),
    )
    node_or_false = LogicalNode(
        left_operand=VarNode(FloatToken('0.0')),
        operator=OrToken('ИЛИ'),
        right_operand=VarNode(FloatToken('0.0')),
    )
    assert str(node_and) == 'LogicalNode (AndToken)'
    assert str(node_or) == 'LogicalNode (OrToken)'

    stack = StackWrapper()
    namespace = NamespaceWrapper()

    node_and.eval(namespace, stack)
    assert stack.pop(node_and) == 1

    node_or.eval(namespace, stack)
    assert stack.pop(node_or) == 1

    node_and_false.eval(namespace, stack)
    assert stack.pop(node_and) == 0

    node_or_false.eval(namespace, stack)
    assert stack.pop(node_or) == 0

    assert node_and.short_name == 'Логическое И'
    assert node_or.short_name == 'Логическое ИЛИ'

    assert serialize_to_text(node_and) == '1.75 and 2.34'
    assert serialize_to_text(node_or) == '0.0 or 0.1'
    assert serialize_to_python(node_and) == 'math_round(1.75, 5) ' \
                                            'and math_round(2.34, 5)'
    assert serialize_to_python(node_or) == 'math_round(0.0, 5) or ' \
                                           'math_round(0.1, 5)'


def test_call_node():
    node = CallNode(NameNode(NameToken('ОКРУГЛ')),
                    VarNode(IntegerToken('3')),
                    VarNode(FloatToken('2.75')))
    assert str(node) == 'CallNode'

    stack = StackWrapper()
    namespace = NamespaceWrapper({'ОКРУГЛ': lambda x, y: x * y ** 2})
    node.eval(namespace, stack)
    assert stack.pop(node) == 22.6875

    assert node.short_name == 'Вызов'

    assert serialize_to_text(node) == 'ОКРУГЛ(3, 2.75)'
    assert serialize_to_python(node) == 'math_round(3, math_round(2.75, 5))'

    with pytest.raises(exceptions.CustomSemanticError,
                       match='Функция с названием "ОКРУГЛ" не найдена.'):
        node.eval(NamespaceWrapper(), stack)

    with pytest.raises(exceptions.CustomSemanticError,
                       match='Объект с названием "ОКРУГЛ" '
                             'не является вызываемым.'):
        node.eval(NamespaceWrapper({'ОКРУГЛ': 25}), stack)


def test_assignment_node():
    node = AssigmentNode(
        left_operand=NameNode(NameToken('test')),
        operator=Assignment('='),
        right_operand=VarNode(IntegerToken('25'))
    )
    assert str(node) == 'AssigmentNode (Assignment)'
    stack = StackWrapper()
    namespace = NamespaceWrapper()
    node.eval(namespace, stack)
    assert namespace.dict() == {'test': 25.0}
    assert node.short_name == 'Присваивание'

    with pytest.raises(exceptions.CustomSemanticError,
                       match='Попытка изменения типа при присвоении значения, '
                             'переменная "test" была <str> а '
                             'присваивается <float>.'):
        node.eval(NamespaceWrapper({'test': 'string'}), stack)

    assert serialize_to_text(node) == 'test = 25;'
    assert serialize_to_python(node) == 'test = 25'


def test_unary_not_node():
    node_1 = UnaryNotNode(VarNode(FloatToken('0.25')))
    node_2 = UnaryNotNode(VarNode(FloatToken('0.0')))

    assert str(node_1) == 'UnaryNotNode (Not)'
    assert str(node_2) == 'UnaryNotNode (Not)'

    stack = StackWrapper()
    namespace = NamespaceWrapper()
    node_1.eval(namespace, stack)
    assert stack.pop(node_1) == 0
    node_2.eval(namespace, stack)
    assert stack.pop(node_2) == 1

    assert node_1.short_name == 'НЕ'
    assert node_2.short_name == 'НЕ'

    assert serialize_to_text(node_1) == 'НЕ 0.25'
    assert serialize_to_text(node_2) == 'НЕ 0.0'
    assert serialize_to_python(node_1) == 'not math_round(0.25, 5)'
    assert serialize_to_python(node_2) == 'not math_round(0.0, 5)'


@pytest.mark.parametrize('left, right, ref, textual, pythonic', [
    ('14.0', '14.0', {'x': 'test'},
     CONDITION_TEXTUAL_1, CONDITION_PYTHONIC_1),
    ('1.0', '14.0', {'x': 'not actually test'},
     CONDITION_TEXTUAL_2, CONDITION_PYTHONIC_2),
    ('0.0', '14.0', {'x': 'really not test'},
     CONDITION_TEXTUAL_3, CONDITION_PYTHONIC_3),
])
def test_condition(left, right, ref, textual, pythonic):
    node = ConditionNode(
        IfNode(
            BinaryNode(
                left_operand=VarNode(FloatToken(left)),
                operator=GE('>='),
                right_operand=VarNode(FloatToken(right))
            ),
            ScopeNode(
                AssigmentNode(
                    left_operand=NameNode(NameToken('x')),
                    operator=Assignment('='),
                    right_operand=VarNode(StringToken('test'))
                ))
        ),
        ElifNode(
            LogicalNode(
                left_operand=VarNode(FloatToken(left)),
                operator=AndToken('and'),
                right_operand=VarNode(FloatToken(right))
            ),
            ScopeNode(
                AssigmentNode(
                    left_operand=NameNode(NameToken('x')),
                    operator=Assignment('='),
                    right_operand=VarNode(StringToken('"not actually test"'))
                )
            )
        ),
        ElseNode(
            ScopeNode(
                AssigmentNode(
                    left_operand=NameNode(NameToken('x')),
                    operator=Assignment('='),
                    right_operand=VarNode(StringToken('"really not test"'))
                )
            )
        )
    )
    assert str(node) == 'ConditionNode'
    assert node.short_name == 'Условие'

    assert str(node.sub_nodes[0]) == 'IfNode (if)'
    assert str(node.sub_nodes[1]) == 'ElifNode (elif)'
    assert str(node.sub_nodes[2]) == 'ElseNode (else)'

    assert node.sub_nodes[0].short_name == 'if'
    assert node.sub_nodes[1].short_name == 'elif'
    assert node.sub_nodes[2].short_name == 'else'

    stack = StackWrapper()
    namespace = NamespaceWrapper()
    node.eval(namespace, stack)
    assert namespace.dict() == ref

    assert serialize_to_text(node) == textual
    assert serialize_to_python(node) == pythonic


def test_par():
    node = ParNode(ParNode(BinaryNode(
        left_operand=VarNode(StringToken("one")),
        operator=Plus('+'),
        right_operand=VarNode(StringToken("two"))
    )))
    assert str(node) == 'ParNode'
    assert node.short_name == 'Круглые скобки'

    assert serialize_to_text(node) == '(("one" + "two"))'
    assert serialize_to_python(node) == '(("one" + "two"))'

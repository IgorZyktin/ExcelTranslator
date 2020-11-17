# -*- coding: utf-8 -*-

"""Инструменты для конверсии нод в текст.
"""
from functools import singledispatch

from exceltranslator.defined_names import translate_script_name
from exceltranslator.lexer.tokens import *
from exceltranslator.parser.base_nodes import *
from exceltranslator.parser.nodes import *
from exceltranslator.settings import DEFAULT_PRECISION, DEFAULT_INDENT


NAME_REPLACEMENTS = {
    # математические
    'СЛЧИС': 'random.random',
    'МИН': 'min',
    'МАКС': 'max',
    'СУММ': 'custom_sum',
    'ABS': 'abs',
    'ОКРУГЛ': 'math_round',
    'ОКРВВЕРХ': 'math.ceil',
    'ОКРВНИЗ': 'math.floor',
    'ЦЕЛОЕ': 'int',
    'ОСТАТ': 'mod',
    'СЛУЧМЕЖДУ': 'random.randint',
    'КОРЕНЬ': 'math.sqrt',
    'ОТБР': 'math.trunc',
    'СРЗНАЧ': 'custom_avg',

    # текстовые
    'СТРОЧН': 'str.lower',
    'ТЕКСТ': 'str',
    'ПРОПИСН': 'str.upper',
    'ЗНАЧЕН': 'float',
    'СЦЕПИТЬ': 'custom_concatenate',
    'ОБЪЕДИНИТЬ': 'custom_join',

    # логические
    'ВСЕ_ИЗ': 'custom_all',
    'ОДИН_ИЗ': 'custom_any',
    'НИ_ОДИН_ИЗ': 'custom_not_any',

    # специальные
    'ТОЧКА': 'rig',
    'СЕЙЧАС': 'now',
    'СЕГОДНЯ': 'today',
    'MQTT': 'mqtt',
    'ОТЧЁТ': 'report',
    'СОХР': 'save',
    'ЗАГР': 'load',
    'СТОП': 'exit',
}


# Базовые функции -------------------------

def serialize_to_text(node) -> str:
    """Разложить в исходный код.
    """
    return _serialize_to_text(node).strip()


def serialize_to_python(node) -> str:
    """Разложить в исходный код на python.
    """
    return _serialize_to_python(node).strip()
    
    
@singledispatch
def _serialize_to_text(node, prefix: str = '') -> str:
    """Разложить в исходный код.
    """


@singledispatch
def _serialize_to_python(node, prefix: str = '') -> str:
    """Разложить в исходный код на python.
    """


# Реализации для текста -------------------------


@_serialize_to_text.register
def _serialize_to_text_variable(node: VarNode, prefix: str = '') -> str:
    """Переменная.
    """
    if type(node.value) == IntegerToken:
        text = node.prefix + node.value.source_code

    elif type(node.value) == FloatToken:
        text = f'{node.prefix}{node.value.source_code}'

    else:
        text = node.value.source_code.lstrip('"' + "'").rstrip("'" + '"')
        text = f'"{text}"'

    return prefix + text


@_serialize_to_text.register
def _serialize_to_text_unary_minus(node: UnaryMinusNode,
                                   prefix: str = '') -> str:
    """Унарный минус.
    """
    return prefix + _serialize_to_text(node.sub_nodes[0])


@_serialize_to_text.register
def _serialize_to_text_unary_not(node: UnaryNotNode, prefix: str = '') -> str:
    """Унарное отрицание.
    """
    return prefix + 'НЕ ' + _serialize_to_text(node.sub_nodes[0])


@_serialize_to_text.register
def _serialize_to_text_name(node: NameNode, prefix: str = '') -> str:
    """Имя.
    """
    return prefix + node.value.source_code


@_serialize_to_text.register
def _serialize_to_text_assignment(node: AssigmentNode,
                                  prefix: str = '') -> str:
    """Присваивание.
    """
    left = _serialize_to_text(node.left_operand)
    right = _serialize_to_text(node.right_operand)
    return f'{prefix}{left} = {right};'


@_serialize_to_text.register
def _serialize_to_text_binary(node: BinaryNode, prefix: str = '') -> str:
    """Бинарный оператор.
    """
    left = _serialize_to_text(node.left_operand)
    right = _serialize_to_text(node.right_operand)
    return prefix + f'{left} {node.operator.figure} {right}'


@_serialize_to_text.register
def _serialize_to_text_call(node: CallNode, prefix: str = '') -> str:
    """Вызов.
    """
    children = []
    for child in node.sub_nodes[1:]:
        children.append(_serialize_to_text(child))

    text = f'{prefix}{node.name.value}(' + ', '.join(children) + ')'

    return text


@_serialize_to_text.register
def _serialize_to_text_instruction(node: InstructionNode,
                                   prefix: str = '') -> str:
    """Инструкция.
    """
    elements = []
    for child in node.sub_nodes:
        elements.append(_serialize_to_text(child, prefix))
    return '\n'.join(elements)


@_serialize_to_text.register
def _serialize_to_text_condition(node: ConditionNode, prefix: str = '') -> str:
    """Условие.
    """
    elements = []
    for child in node.sub_nodes:
        elements.append(_serialize_to_text(child, prefix))
    return prefix + ''.join(elements) + ';'


@_serialize_to_text.register
def _serialize_to_text_if(node: IfNode, prefix: str = '') -> str:
    """Условие if.
    """
    left = _serialize_to_text(node.predicate)
    right = _serialize_to_text(node.sub_scope, prefix)
    return f'ЕСЛИ ({left})\n{right}'


@_serialize_to_text.register
def _serialize_to_text_elif(node: ElifNode, prefix: str = '') -> str:
    """Условие elif.
    """
    left = _serialize_to_text(node.predicate)
    right = _serialize_to_text(node.sub_scope, prefix)
    return f'\n{prefix}ИНАЧЕ_ЕСЛИ ({left})\n{right}'


@_serialize_to_text.register
def _serialize_to_text_else(node: ElseNode, prefix: str = '') -> str:
    """Условие else.
    """
    text = _serialize_to_text(node.sub_scope, prefix)
    return f'\n{prefix}ИНАЧЕ\n{text}'


@_serialize_to_text.register
def _serialize_to_text_scope(node: ScopeNode, prefix: str = '') -> str:
    """Области видимости.
    """
    text = _serialize_to_text(node.sub_nodes[0], prefix + DEFAULT_INDENT)
    return f'{prefix}{{\n{text}\n{prefix}}}'


@_serialize_to_text.register
def _serialize_to_text_par(node: ParNode, prefix: str = '') -> str:
    """Скобки.
    """
    text = _serialize_to_text(node.sub_nodes[0], prefix)
    return f'({text})'


# Реализации для python -------------------------


@_serialize_to_python.register
def _serialize_to_python_variable(node: VarNode, prefix: str = '') -> str:
    """Переменная.
    """
    if type(node.value) == IntegerToken:
        text = node.prefix + node.value.source_code

    elif type(node.value) == FloatToken:
        text = f'math_round({node.prefix}{node.value.source_code}, ' \
               f'{DEFAULT_PRECISION})'

    else:
        text = node.value.source_code.lstrip('"' + "'").rstrip("'" + '"')
        text = f'"{text}"'

    return prefix + text


@_serialize_to_python.register
def _serialize_to_python_unary_minus(node: UnaryMinusNode,
                                     prefix: str = '') -> str:
    """Унарный минус.
    """
    return prefix + _serialize_to_python(node.sub_nodes[0])


@_serialize_to_python.register
def _serialize_to_python_unary_not(node: UnaryNotNode,
                                   prefix: str = '') -> str:
    """Унарное отрицание.
    """
    return prefix + 'not ' + _serialize_to_python(node.sub_nodes[0])


@_serialize_to_python.register
def _serialize_to_python_name(node: NameNode, prefix: str = '') -> str:
    """Имя.
    """
    return prefix + node.value.source_code


@_serialize_to_python.register
def _serialize_to_python_binary(node: BinaryNode, prefix: str = '') -> str:
    """Бинарный оператор.
    """
    left = _serialize_to_python(node.left_operand)
    right = _serialize_to_python(node.right_operand)
    return prefix + f'{left} {node.operator.figure} {right}'


@_serialize_to_python.register
def _serialize_to_python_call(node: CallNode, prefix: str = '') -> str:
    """Вызов.
    """
    children = []
    for child in node.sub_nodes[1:]:
        children.append(_serialize_to_python(child))

    original_name = str(node.name.value)
    new_name = NAME_REPLACEMENTS.get(original_name, f'?{original_name}?')

    if new_name == 'rig':
        children[1] = '"' + translate_script_name(
            children[1].strip('"').strip("'")
        ) + '"'

    elif new_name in ('now', 'today'):
        for i, child in enumerate(children):
            children[i] = '"' + translate_script_name(child.strip('"').strip("'")
                                                      ) + '"'

    text = f'{prefix}{new_name}(' + ', '.join(children) + ')'

    return text


@_serialize_to_python.register
def _serialize_to_python_assignment(node: AssigmentNode,
                                    prefix: str = '') -> str:
    """Присваивание.
    """
    left = _serialize_to_python(node.left_operand)
    right = _serialize_to_python(node.right_operand)
    return f'{prefix}{left} = {right}'


@_serialize_to_python.register
def _serialize_to_python_condition(node: ConditionNode,
                                   prefix: str = '') -> str:
    """Условие.
    """
    elements = []
    for child in node.sub_nodes:
        elements.append(_serialize_to_python(child, prefix))
    return ''.join(elements)


@_serialize_to_python.register
def _serialize_to_python_if(node: IfNode, prefix: str = '') -> str:
    """Условие if.
    """
    left = _serialize_to_python(node.predicate)
    right = _serialize_to_python(node.sub_scope, prefix)
    return f'{prefix}if {left}:\n{right}'


@_serialize_to_python.register
def _serialize_to_python_elif(node: ElifNode, prefix: str = '') -> str:
    """Условие elif.
    """
    left = _serialize_to_python(node.predicate)
    right = _serialize_to_python(node.sub_scope, prefix)
    return f'\n\n{prefix}elif {left}:\n{right}'


@_serialize_to_python.register
def _serialize_to_python_else(node: ElseNode, prefix: str = '') -> str:
    """Условие else.
    """
    text = _serialize_to_python(node.sub_scope, prefix)
    return f'\n\n{prefix}else:\n{text}\n'


@_serialize_to_python.register
def _serialize_to_python_scope(node: ScopeNode, prefix: str = '') -> str:
    """Области видимости.
    """
    text = _serialize_to_python(node.sub_nodes[0], prefix + DEFAULT_INDENT)
    return f'{text}'


@_serialize_to_python.register
def _serialize_to_python_par(node: ParNode, prefix: str = '') -> str:
    """Скобки.
    """
    text = _serialize_to_python(node.sub_nodes[0], prefix)
    return f'({text})'


@_serialize_to_python.register
def _serialize_to_python_instruction(node: InstructionNode,
                                     prefix: str = '') -> str:
    """Инструкция.
    """
    elements = []
    for child in node.sub_nodes:
        text = _serialize_to_python(child, prefix)
        elements.append(text)

    return '\n'.join(elements)

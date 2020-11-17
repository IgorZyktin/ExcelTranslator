# -*- coding: utf-8 -*-

"""Звенья абстрактного синтаксического дерева.
"""
from typing import Callable, List, cast, Union

from exceltranslator.defined_names import FuncWrapper
from exceltranslator.exceptions import CustomSemanticError
from exceltranslator.helpers.namespace_wrapper import NamespaceWrapper
from exceltranslator.helpers.stack_wrapper import StackWrapper
from exceltranslator.lexer.base_tokens import *
from exceltranslator.lexer.tokens import *
from exceltranslator.parser.base_nodes import *
from exceltranslator.settings import DEFAULT_PRECISION

__all__ = [
    'BinaryNode',
    'ConditionNode',
    'UnaryNotNode',
    'NameNode',
    'UnaryMinusNode',
    'LogicalNode',
    'CallNode',
    'AssigmentNode',
    'VarNode',
]

from exceltranslator.utils import math_round, AsIsMixin


class BinaryNode(BaseBinaryNode):
    """Узел для бинарных операторов.
    """

    def eval(self, namespace: NamespaceWrapper,
             stack: StackWrapper, depth: int = 0) -> None:
        """Исполнить код в узле и всех потомках.
        """
        self.left_operand.eval(namespace, stack, depth=depth + 1)
        left = stack.pop(self)

        self.right_operand.eval(namespace, stack, depth=depth + 1)
        right = stack.pop(self)

        if self.operator.figure == '/' and right == 0:
            self.propagate(
                'zero_division',
                location=f'{self}._evaluate',
                operation=f'{self.left_operand} / {self.right_operand}'
            )
            result = float('inf')

        else:
            self.propagate('operator_use', location=f'{self}._evaluate',
                           operator=self.operator.figure,
                           operation=f'{self.left_operand} '
                                     f'{self.operator.figure} '
                                     f'{self.right_operand}')

            if (isinstance(left, (int, float)) and isinstance(right,
                                                              (int, float))) \
                    or (type(left) == str and type(right) == str):
                result = self.operator.callable(left, right)

            else:
                raise CustomSemanticError(
                    f'Нельзя осуществлять операцию {left!r} '
                    f'{self.operator.figure} {right!r}'
                )

        if isinstance(result, float):
            result = math_round(result, DEFAULT_PRECISION)

        stack.append(self, result)


class LogicalNode(BinaryNode):
    """Узел для логических операторов.

    Аналогично бинарным, но возвращает 0 и 1.
    """

    def eval(self, namespace: NamespaceWrapper, stack: StackWrapper,
             depth: int = 0) -> None:
        """Исполнить код в узле и всех потомках.
        """
        self.left_operand.eval(namespace, stack, depth=depth + 1)
        left = stack.pop(self)

        self.right_operand.eval(namespace, stack, depth=depth + 1)
        right = stack.pop(self)

        self.propagate('operator_use', location=f'{self}._evaluate',
                       operator=self.operator.figure,
                       operation=f'{self.left_operand} '
                                 f'{self.operator.figure} '
                                 f'{self.right_operand}')

        if type(self.operator) in (AndToken, OrToken):
            left = bool(left)
            right = bool(right)

        result = int(self.operator.callable(left, right))

        stack.append(self, result)


class ConditionNode(BaseNode, AsIsMixin):
    """Условие.
    """

    def eval(self, namespace: NamespaceWrapper, stack: StackWrapper,
             depth: int = 0) -> None:
        """Проверить условие.
        """
        self.sub_nodes = cast(List[BaseCondition], self.sub_nodes)
        if_node = self.sub_nodes[0]

        if if_node.bool(namespace, stack, depth=depth + 1):
            if_node.sub_scope.eval(namespace, stack, depth=depth + 1)
            return

        for child in self.sub_nodes[1:]:
            if type(child) == ElifNode:

                if child.bool(namespace, stack, depth=depth + 1):
                    child.sub_scope.eval(namespace, stack, depth=depth + 1)
                    return
            else:
                child.sub_scope.eval(namespace, stack, depth=depth + 1)
                return


class VarNode(BaseNode):
    """Узел для объектов, которые могут быть вызваны на месте операторов.
    """

    def __init__(self, value: BaseToken) -> None:
        """Инициализировать экземпляр.
        """
        super().__init__()
        self.value = value
        self.prefix = ''

    def __repr__(self):
        """Вернуть текстовое представление.
        """
        value = self.value.source_code
        if isinstance(self.value, (StringToken, NameToken)):
            value = self.value.source_code.lstrip('"' + "'").rstrip("'" + '"')
            value = f'"{value}"'
        return super().__repr__() + f' (value={self.prefix}{value})'

    @property
    def short_name(self) -> str:
        """Короткое название (для целей распечатки).
        """
        return f'{self.prefix}{self.value}'

    def eval(self, namespace: NamespaceWrapper, stack: StackWrapper,
             depth: int = 0) -> None:
        """Исполнить код в узле и всех потомках.
        """
        if type(self.value) in (IntegerToken, FloatToken):
            new_value = math_round(float(self.prefix + self.value.source_code),
                                   DEFAULT_PRECISION)

        elif type(self.value) == StringToken:
            new_value = self.value.source_code.lstrip('"' + "'").rstrip(
                "'" + '"')

        else:
            raise CustomSemanticError(
                f'Неизвестный тип переменной: {self.value}, {type(self.value)}'
            )

        stack.append(self, new_value)


class NameNode(VarNode):
    """Ссылка на имя.
    """

    @property
    def short_name(self) -> str:
        """Короткое название (для целей распечатки).
        """
        return f'Имя({self.value.source_code})'

    def eval(self, namespace: NamespaceWrapper, stack: StackWrapper,
             depth: int = 0) -> None:
        """Исполнить код в узле и всех потомках.
        """
        name = self.value.source_code
        variable = namespace.get(self, name)

        if variable is None:
            raise CustomSemanticError(
                f'Переменная с именем "{name}" не найдена.')

        if isinstance(variable, float):
            variable = math_round(variable, DEFAULT_PRECISION)

        stack.append(self, variable)


class UnaryMinusNode(BaseNode, AsIsMixin):
    """Унарный минус.
    """

    def __init__(self, *args: 'BaseNode') -> None:
        """Инициализировать экземпляр.
        """
        self.prefix = '-'
        for arg in args:
            arg.prefix = self.prefix

        super().__init__(*args)


class UnaryNotNode(BaseNode):
    """Отрицание.
    """

    @property
    def short_name(self) -> str:
        """Короткое название (для целей распечатки).
        """
        return f'НЕ'

    def __repr__(self):
        """Вернуть текстовое представление.
        """
        return super().__repr__() + f' (Not)'

    def eval(self, namespace: NamespaceWrapper, stack: StackWrapper,
             depth: int = 0) -> None:
        """Исполнить код в узле и всех потомках.
        """
        self.sub_nodes[0].eval(namespace, stack, depth=depth + 1)
        value = stack.pop(self)
        result = int(not value)
        stack.append(self, result)


class AssigmentNode(BinaryNode):
    """Присваивание.
    """

    def __init__(self, left_operand: NameNode, operator: Assignment,
                 right_operand: Union[BaseNode, 'BaseBinaryNode']):
        """Инициализировать экземпляр.
        """
        operator = cast(BinaryToken, operator)
        super().__init__(left_operand, operator, right_operand)

    @property
    def left_operand(self) -> VarNode:
        """Первый потомок.
        """
        return cast(VarNode, self.sub_nodes[0])

    def eval(self, namespace: NamespaceWrapper, stack: StackWrapper,
             depth: int = 0) -> None:
        """Исполнить код в узле и всех потомках.
        """
        name = self.left_operand.value.source_code

        self.right_operand.eval(namespace, stack, depth=depth + 1)
        value = stack.pop(self)

        existing = namespace.get(self, name)

        all_numbers = all(
            isinstance(x, (int, float)) for x in [value, existing])

        if existing is not None \
                and not all_numbers \
                and not isinstance(value, type(existing)):
            new_type = type(value).__name__
            existing_type = type(existing).__name__

            raise CustomSemanticError(
                f'Попытка изменения типа при присвоении значения, '
                f'переменная "{name}" была '
                f'<{existing_type}> а присваивается <{new_type}>.'
            )

        namespace.set(self, name, value)


class CallNode(BaseNode):
    """Вызов.
    """

    def __init__(self, name: VarNode, *args: BaseNode) -> None:
        """Инициализировать экземпляр.
        """
        self.name = name
        super().__init__(name, *args)

    def eval(self, namespace: NamespaceWrapper, stack: StackWrapper,
             depth: int = 0) -> None:
        """Исполнить код в узле и всех потомках.
        """
        name = self.name.value.source_code

        operands = []
        for child in self.sub_nodes[1:]:  # первый потомок это имя
            child.eval(namespace, stack, depth=depth + 1)
            operands.append(stack.pop(self))

        function: FuncWrapper = namespace.get(self, name)

        if function is None:
            raise CustomSemanticError(
                f'Функция с названием "{name}" не найдена.')

        if not isinstance(function, Callable):
            raise CustomSemanticError(
                f'Объект с названием "{name}" не является вызываемым.')

        self.propagate('call', name=name, location=f'{self}._evaluate',
                       operand=[str(x) for x in operands])

        result = function(*operands)
        stack.append(self, result)

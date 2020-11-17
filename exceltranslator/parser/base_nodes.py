# -*- coding: utf-8 -*-

"""Базовые звенья абстрактного синтаксического дерева.
"""
from abc import ABC
from typing import List, Generator, Tuple, Any, Union

from exceltranslator.exceptions import CustomSemanticError
from exceltranslator.helpers.informer import Informer
from exceltranslator.helpers.namespace_wrapper import NamespaceWrapper
from exceltranslator.helpers.stack_wrapper import StackWrapper
from exceltranslator.helpers.watcher import Watcher
from exceltranslator.lexer.base_tokens import BinaryToken
from exceltranslator.utils import AsIsMixin

__all__ = [
    'BaseNode',
    'BaseBinaryNode',
    'ParNode',
    'StopNode',
    'ScopeNode',
    'InstructionNode',
    'IfNode',
    'ElifNode',
    'ElseNode',
    'BaseCondition',
]


class BaseNode(Informer, AsIsMixin, ABC):
    """Базовый класс узла.
    """

    def __init__(self, *nodes: 'BaseNode', parent: 'BaseNode' = None,
                 number: int = 1, watcher: Watcher = None) -> None:
        """Инициализировать экземпляр.
        """
        super().__init__(parent, watcher)
        self.sub_nodes: List['BaseNode'] = []
        self.number = number
        self.parent = parent
        self.add_nodes(*nodes)

    def __repr__(self):
        """Вернуть текстовое представление.
        """
        return type(self).__name__

    def total_relatives(self) -> int:
        """Вернуть количество нод у родителя.
        """
        if not self.parent:
            return 1
        return len(self.parent.sub_nodes)

    def add_nodes(self, *nodes: 'BaseNode'):
        """Добавить один элемент в листьевые узлы.
        """
        for node in nodes:
            node.parent = self
            node.number = len(self.sub_nodes) + 1
            self.sub_nodes.append(node)

    def iter_recursively(self, depth: int = 0)\
            -> Generator[Tuple['BaseNode', dict], None, None]:
        """Итерироваться по всем потомкам.
        """
        yield self, depth
        for i, child in enumerate(self.sub_nodes, start=1):
            yield from child.iter_recursively(depth + 1)

    def evaluate(self, namespace: NamespaceWrapper = None,
                 stack: StackWrapper = None) -> Any:
        """Исполнить код в узле и всех потомках.

        Эта функция доступна снаружи.
        """
        namespace = namespace if namespace is not None else NamespaceWrapper()
        stack = stack if stack is not None else StackWrapper()
        self.eval(namespace, stack, depth=0)

        if stack:
            return stack.pop(self)
        return None

    def eval(self, namespace: NamespaceWrapper,
             stack: StackWrapper, depth: int = 0) -> None:
        """Исполнить код в узле и всех потомках.
        """
        for node in self.sub_nodes:
            node.eval(namespace, stack, depth=depth + 1)


class BaseBinaryNode(BaseNode, ABC):
    """Спецальный класс, для нод с двумя (и только двумя) операндами.
    """

    def __init__(self, left_operand: Union[BaseNode, 'BaseBinaryNode'],
                 operator: BinaryToken,
                 right_operand: Union[BaseNode, 'BaseBinaryNode']):
        """Инициализировать экземпляр.
        """
        super().__init__(left_operand, right_operand)
        self.operator = operator

        if len(self.sub_nodes) != 2:
            raise CustomSemanticError(
                'Бинарный оператор может работать только с двумя узлами.'
            )

    def __repr__(self):
        """Вернуть текстовое представление.
        """
        return super().__repr__() + f' ({type(self.operator).__name__})'

    @property
    def left_operand(self) -> BaseNode:
        """Первый потомок.
        """
        return self.sub_nodes[0]

    @property
    def right_operand(self) -> BaseNode:
        """Последний (по идее второй) потомок.
        """
        return self.sub_nodes[-1]

    @property
    def short_name(self) -> str:
        """Короткое название (для целей распечатки).
        """
        return self.operator.short_name


class InstructionNode(BaseNode):
    """Инструкция.
    """


class EmptyNode(BaseNode):
    """Пустая нода.
    """


class StopNode(BaseNode):
    """Остановка.
    """


class ParNode(BaseNode):
    """Круглые скобки.
    """


class ScopeNode(BaseNode):
    """Фигурные скобки.
    """


class BaseCondition(BaseNode):
    """Условие.
    """

    def bool(self, namespace: NamespaceWrapper,
             stack: StackWrapper, depth: int):
        """Проверка истинности.
        """
        return self.eval(namespace, stack, depth)

    @property
    def predicate(self) -> BaseNode:
        """Собственно логическая часть условия.
        """
        return self.sub_nodes[0]

    @property
    def sub_scope(self) -> BaseNode:
        """Собственно логическая часть условия.
        """
        return self.sub_nodes[1]

    def eval(self, namespace: NamespaceWrapper,
             stack: StackWrapper, depth: int = 0):
        """Проверить условие.
        """
        self.predicate.eval(namespace, stack, depth=depth + 1)
        result = stack.pop(self)
        return result


class IfNode(BaseCondition):
    """Условие, нода для if.
    """

    def __repr__(self):
        """Вернуть текстовое представление.
        """
        return super().__repr__() + ' (if)'

    @property
    def short_name(self) -> str:
        """Короткое название (для целей распечатки).
        """
        return 'if'


class ElifNode(BaseCondition):
    """Условие, нода для elif.
    """

    @property
    def short_name(self) -> str:
        """Короткое название (для целей распечатки).
        """
        return 'elif'

    def __repr__(self):
        """Вернуть текстовое представление.
        """
        return super().__repr__() + f' (elif)'


class ElseNode(BaseCondition):
    """Условие, нода для else.
    """

    @property
    def short_name(self) -> str:
        """Короткое название (для целей распечатки).
        """
        return 'else'

    @property
    def predicate(self) -> None:
        """Не имеет своего условия.
        """
        return None

    @property
    def sub_scope(self) -> BaseNode:
        """Содержит только под-область.
        """
        return self.sub_nodes[0]

    def __repr__(self):
        """Вернуть текстовое представление.
        """
        return super().__repr__() + f' (else)'

    def eval(self, namespace: NamespaceWrapper,
             stack: StackWrapper, depth: int = 0):
        """Исполнить наследников.
        """
        self.sub_scope.eval(namespace, stack, depth=depth + 1)
        result = stack.pop(self)
        return result

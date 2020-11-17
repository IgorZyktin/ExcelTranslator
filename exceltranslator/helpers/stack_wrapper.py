# -*- coding: utf-8 -*-

"""Обёртка над очередью. Оповещает о событиях.
"""
from collections import deque
from typing import Any

from exceltranslator.helpers.informer import Informer
from exceltranslator.helpers.watcher import Watcher


class StackWrapper(Informer):
    """Обёртка над очередью. Оповещает о событиях.
    """

    def __init__(self, parent: 'Informer' = None, watcher: Watcher = None):
        """Инициализировать экземпляр.
        """
        super().__init__(parent, watcher)
        self._stack = deque()

    def __bool__(self):
        """Истинен когда не пуст.
        """
        return bool(self._stack)

    def __repr__(self):
        """Вернуть текстовое представление.
        """
        return type(self).__name__ + f'({self._stack})'

    def pop(self, caller: Any) -> Any:
        """Снять верхушку стека и сообщить об этом куда надо.
        """
        value = self._stack.pop()
        self.propagate(
            'stack_pop',
            value=value,
            caller=str(caller),
            caller_id=id(caller),
            size=len(self._stack),
        )
        return value

    def append(self, caller: Any, value: Any) -> None:
        """Положить на верхушку стека и сообщить об этом куда надо.
        """
        self._stack.append(value)
        self.propagate(
            'stack_append',
            value=value,
            caller=str(caller),
            caller_id=id(caller),
            size=len(self._stack),
        )

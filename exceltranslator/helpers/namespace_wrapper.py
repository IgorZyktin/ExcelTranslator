# -*- coding: utf-8 -*-

"""Обёртка над словарём. Оповещает о событиях.
"""
from typing import Any

from exceltranslator.defined_names import get_default_names
from exceltranslator.exceptions import CustomSyntaxError
from exceltranslator.helpers.informer import Informer
from exceltranslator.helpers.watcher import Watcher


class NamespaceWrapper(Informer):
    """Обёртка над словарём. Оповещает о событиях.
    """

    def __init__(self,
                 contents: dict = None,
                 parent: 'Informer' = None,
                 watcher: Watcher = None):
        """Инициализировать экземпляр.
        """
        super().__init__(parent, watcher)
        self._dict = contents or {}

    def __bool__(self):
        """Истинен когда не пуст.
        """
        return bool(self._dict)

    def __getitem__(self, item):
        """Извлечь элемент.
        """
        return self.get(None, item)

    def __repr__(self):
        """Вернуть текстовое представление.
        """
        return type(self).__name__ + f'({self._dict})'

    def clear(self):
        """Очистить внутренний словарь.
        """
        self._dict.clear()

    def get(self, caller: Any, key: Any, default: Any = None) -> Any:
        """Получить значение по ключу и сообщить об этом куда надо.
        """
        output = self._dict.get(key, default)
        self.propagate(
            'namespace_get',
            value=output,
            key=key,
            default=default,
            caller_id=id(caller)
        )
        return output

    def set(self, caller: Any, key, value):
        """Внести значение по ключу и сообщить об этом куда надо.
        """
        existing = self._dict.get(key)

        if existing is None:
            self.propagate(
                'namespace_assign',
                value=value,
                key=key,
                caller_id=id(caller)
            )
        else:
            self.propagate(
                'namespace_overwrite',
                previous_value=existing,
                value=value,
                key=key,
                caller_id=id(caller)
            )

        if str(key) and str(key)[0].isdigit():
            raise CustomSyntaxError(
                f'Для переменных допускатся только имена, '
                f'начинающиеся не с цифры. {key} не подойдёт.'
            )

        self._dict[key] = value

    def dict(self):
        """Содержимое.
        """
        return self._dict.copy()


class Namespace(NamespaceWrapper):
    """Обёртка с уже подготовленными функциями внутри.
    """

    def __init__(self, contents: dict = None, parent: 'Informer' = None,
                 watcher: Watcher = None):
        """Инициализировать экземпляр.
        """
        super().__init__(contents, parent, watcher)
        if contents is None:
            contents = {}

        self._dict = {**get_default_names(), **contents}

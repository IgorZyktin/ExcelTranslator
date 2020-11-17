# -*- coding: utf-8 -*-

"""Класс, оповещающий о своих изменениях.
"""
from exceltranslator.helpers.watcher import Watcher


class Informer:
    """Класс, оповещающий о своих изменениях.
    """

    def __init__(self, parent: 'Informer' = None, watcher: Watcher = None):
        """Инициализировать экземпляр.
        """
        self.watcher = watcher
        self.parent = parent

    def propagate(self, header: str, **kwargs):
        """Сообщить наблюдателю о событии.
        """
        if self.watcher:
            self.watcher.inform(header, **kwargs)

        elif self.parent:
            self.parent.propagate(header, **kwargs)

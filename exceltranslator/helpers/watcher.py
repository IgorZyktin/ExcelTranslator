# -*- coding: utf-8 -*-

"""Специальный класс для отлеживания событий ноды.
"""
from collections import deque


class Watcher:
    """Специальный класс для отлеживания событий ноды.
    """

    def __init__(self):
        """Инициализировать экземпляр.
        """
        self.history = deque()

    def inform(self, header: str, **kwargs):
        """Записать событие.
        """
        self.history.append((header, kwargs))

    def make_report(self) -> dict:
        """Сформировать отчёт о событиях.
        """
        report = {
            'stack': {
                'append': 0,
                'pop': 0,
                'max_size': 0,
            },
            'namespace': {
                'get': 0,
                'assign': 0,
                'overwrite': 0,
                'names': [],
                'names_get': set(),
                'names_overwrite': set(),
                'names_assign': set(),
            },
        }
        for header, kwargs in self.history:
            if header == 'stack_append':
                report['stack']['append'] += 1
                report['stack']['max_size'] = max(report['stack']['max_size'],
                                                  kwargs['size'])

            if header == 'stack_pop':
                report['stack']['pop'] += 1
                report['stack']['max_size'] = max(report['stack']['max_size'],
                                                  kwargs['size'])

            if header == 'namespace_get':
                report['namespace']['get'] = report['namespace']['get'] + 1
                report['namespace']['names_get'].add(kwargs['key'])

            if header == 'namespace_overwrite':
                report['namespace']['overwrite'] \
                    = report['namespace']['overwrite'] + 1
                report['namespace']['names_overwrite'].add(kwargs['key'])

            if header == 'namespace_assign':
                report['namespace']['assign'] \
                    = report['namespace']['assign'] + 1
                report['namespace']['names_assign'].add(kwargs['key'])

            report['namespace']['names'] = sorted(
                {
                    *report['namespace']['names_get'],
                    *report['namespace']['names_overwrite'],
                    *report['namespace']['names_assign']
                }
            )

        return report

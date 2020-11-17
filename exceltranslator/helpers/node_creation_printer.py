# -*- coding: utf-8 -*-

"""Специальный класс для вывода нод на печать.
"""
from typing import Callable, Tuple

from colorama import Fore, init

from exceltranslator.parser.parser import Parser, VarNode
from exceltranslator.parser.base_nodes import BaseNode

init(autoreset=True)

DEFAULT_PALETTE = {
    ('in', 'tier_8'): Fore.GREEN,
    ('out', 'tier_8'): Fore.GREEN,

    ('in', 'tier_7'): Fore.GREEN,
    ('out', 'tier_7'): Fore.GREEN,

    ('in', 'tier_6'): Fore.CYAN,
    ('out', 'tier_6'): Fore.CYAN,

    ('in', 'tier_5'): Fore.CYAN,
    ('out', 'tier_5'): Fore.CYAN,

    ('in', 'tier_4'): Fore.CYAN,
    ('out', 'tier_4'): Fore.CYAN,

    ('in', 'tier_3'): Fore.CYAN,
    ('out', 'tier_3'): Fore.CYAN,

    ('in', 'tier_2'): Fore.CYAN,
    ('out', 'tier_2'): Fore.CYAN,

    ('in', 'tier_1'): Fore.CYAN,
    ('out', 'tier_1'): Fore.CYAN,

    ('in', 'tier_0'): Fore.YELLOW,
    ('out', 'tier_0'): Fore.YELLOW,

    'highlight': Fore.RED,
}
DEFAULT_END = Fore.RESET
MAX_TOKENS = 10


class NodeCreationPrinter:
    """Специальный класс для вывода нод на печать.
    """

    def __init__(self, parser: Parser, palette: dict = None,
                 colored: bool = True, with_id: bool = False):
        """Инициализировать экземпляр.
        """
        self.parser = parser
        self.call_stack = []

        target_methods = [x for x in dir(parser) if x.startswith('tier_')]
        for method in target_methods:
            setattr(self.parser,
                    method,
                    self.decorate_method(getattr(parser, method)))

        self.colored = colored
        if colored:
            self.palette = palette or DEFAULT_PALETTE
            self.end = DEFAULT_END
        else:
            self.palette = {}
            self.end = ''

        self.with_id = with_id
        self.default_color = ''
        self.max_tokens = MAX_TOKENS

    @classmethod
    def apply(cls, parser: Parser):
        """Обернуть нужные методы ведомого объекта.
        """
        instance = cls(parser)
        return instance

    def make_stack_line(self, pair: Tuple[str, str], depth: int,
                        prefix: str, suffix: str,
                        separator: str = '-', rest: str = ''):
        """Собрать одну линию погружения/всплытия.
        """
        text = f'depth={depth:02d}, ' \
               + prefix + depth * separator + suffix + rest
        text = self.palette.get(pair, self.default_color) + text + self.end
        return text

    def make_in_line(self, name: str, depth: int) -> str:
        """Погружение в стек.
        """
        tokens_left = self.parser.lexer.tokens_left

        total = len(tokens_left)
        if total > self.max_tokens:
            tokens = ' '.join(tokens_left[:self.max_tokens]) + ' ...'
        else:
            tokens = ' '.join(tokens_left)

        next_token = self.parser.lexer.show_next()
        highlight = self.palette.get('highlight', self.default_color)
        rest = f' {highlight}{next_token}, ' \
               f'ост. {total}:{self.end} {tokens}{self.end}'
        output = self.make_stack_line(('in', name), depth,
                                      f'{name} >', '>', '-', rest)
        return output

    def make_out_line(self, name: str, depth: int, node: BaseNode) -> str:
        """Всплытие из стека.
        """
        if self.with_id:
            id_str = f', id={id(node)}'
        else:
            id_str = ''

        if isinstance(node, VarNode):
            rest = f' {node}{id_str}, value={node.value}'
        else:
            children = [x.short_name for x in node.sub_nodes]
            rest = f' {node}{id_str}, children={children}'

        output = self.make_stack_line(('out', name), depth,
                                      f'{name} <', '<', '=', rest)
        return output

    def decorate_method(self, func: Callable) -> Callable:
        """Обернуть один метод ведомого объекта.
        """

        def wrapper(depth: int):
            """Обёртка над родным методом.
            """
            self.call_stack.append(self.make_in_line(func.__name__,
                                                     depth))
            node = func(depth)
            self.call_stack.append(self.make_out_line(func.__name__,
                                                      depth, node))
            return node

        return wrapper

    def parse(self):
        """Собрать синтаксическое дерево из кода.
        """
        return self.parser.tier_8(depth=0)

    def format_call_stack(self) -> str:
        """Выдать стек вызовов в виде строки.

        Пример данных на входе (список строк):
        [
            'depth=00, tier_8 >> (, ост. 63: (, (, 23, *, 48, ), -, 74, ...',
            'depth=01, tier_7 >-> (, ост. 63: (, (, 23, *, 48, ), -, 74, ...',
            'depth=02, tier_6 >--> (, ост. 63: (, (, 23, *, 48, ), -, 74, ...',
            ...,
        ]

        Пример результата (строка):
        [  1/316] depth=00, tier_8 >> (, ост. 63: (, (, 23, *, 48, ), ...
        [  2/316] depth=01, tier_7 >-> (, ост. 63: (, (, 23, *, 48, ), ...
        [  3/316] depth=02, tier_6 >--> (, ост. 63: (, (, 23, *, 48, ), ...
        [  4/316] depth=03, tier_5 >---> (, ост. 63: (, (, 23, *, 48, ), ...
        """
        total = len(self.call_stack)
        width = len(str(total))
        to_output = [
            '[{number:{width}}/{total:{width}}] {line}'.format(
                width=width,
                number=i,
                total=total,
                line=line
            )
            for i, line in enumerate(self.call_stack, start=1)
        ]
        output = '\n'.join(to_output)
        return output

# -*- coding: utf-8 -*-

"""Специальный класс для вывода нод на печать.
"""
from typing import List, Any, Callable

from colorama import Fore, init

from exceltranslator.parser.base_nodes import (
    BaseNode, InstructionNode, ParNode, ScopeNode, IfNode,
    ElifNode, ElseNode,
)
from exceltranslator.parser.nodes import *

init(autoreset=True)

DEFAULT_LINE = '─'
DEFAULT_EDGE = '└'
DEFAULT_VERT = '│'
DEFAULT_SECTION = '├'
DEFAULT_SPACE = ' '
DEFAULT_SPACE_BLOCKS = 6
DEFAULT_LINE_BLOCKS = 5
JUST_IN_CASE = 2

DEFAULT_PALETTE = {
    CallNode: Fore.LIGHTGREEN_EX,
    InstructionNode: Fore.GREEN,
    NameNode: Fore.LIGHTGREEN_EX,
    AssigmentNode: Fore.LIGHTMAGENTA_EX,
    VarNode: Fore.CYAN,

    BinaryNode: Fore.RED,
    LogicalNode: Fore.LIGHTRED_EX,
    UnaryNotNode: Fore.LIGHTRED_EX,

    UnaryMinusNode: Fore.LIGHTCYAN_EX,

    ConditionNode: Fore.LIGHTBLUE_EX,
    IfNode: Fore.LIGHTBLUE_EX,
    ElifNode: Fore.LIGHTBLUE_EX,
    ElseNode: Fore.LIGHTBLUE_EX,

    ParNode: Fore.YELLOW,
    ScopeNode: Fore.YELLOW,
}


class NodeTreePrinter:
    """Специальный класс для вывода дерева нод на печать.
    """

    def __init__(self, colored: bool = True, with_id: bool = False,
                 with_short_names: bool = True, with_number: bool = False,
                 palette: dict = None):
        """Инициализировать экземпляр.
        """
        self.line = DEFAULT_LINE
        self.edge = DEFAULT_EDGE
        self.vert = DEFAULT_VERT
        self.section = DEFAULT_SECTION
        self.space = DEFAULT_SPACE
        self.line_blocks = DEFAULT_LINE_BLOCKS
        self.space_blocks = DEFAULT_SPACE_BLOCKS

        self.colored = colored
        self.with_id = with_id
        self.with_short_names = with_short_names
        self.with_number = with_number

        if colored:
            self.palette = palette or DEFAULT_PALETTE
            self.end = Fore.RESET
            self.default_color = Fore.LIGHTBLACK_EX
        else:
            self.palette = {}
            self.end = ''
            self.default_color = ''

    def __call__(self, node: BaseNode,
                 print_callable: Callable = None) -> None:
        """Вывести дерево на экран.
        """
        description = self.describe(node)
        print_callable = print_callable or print
        print_callable(description)

    def wrap_in_color(self, node: Any) -> str:
        """Получить цвет для отображения.
        """
        text = str(node)
        if self.with_short_names:
            text = node.short_name

        if self.with_id:
            text = f'{text}-{id(node)}'

        if self.with_number:
            text = f'[{node.number}/{node.total_relatives()}] {text}'

        return self.palette.get(type(node), self.default_color) \
               + text + self.end

    def output_head(self, spacer: str, node) -> str:
        """Распечатать голову ноды.
        """
        return spacer + self.wrap_in_color(node)

    def form_beads(self, visibility_mask: List[int],
                   node: BaseNode, depth: int) -> List[str]:
        """Сформировать списк символов, которые будут выступать префиксами.

        Для таблицы вида:
            BinOpNode-49481592 (Plus)
                    ├─BinOpNode-49481568 (Plus)
                    │     ├─VariableNode-49481616 (value=1)
                    │     └─BinOpNode-49481664 (Multiply)
                    │           ├─VariableNode-49481712 (value=2)
                    │           └─VariableNode-49481760 (value=3)
                    └─VariableNode-49481832 (value=1)

        Бусины будут иметь вид:
            [' ', ' ', ' ', ' ', ' ', ' ', ' ']
            [' ', '├', '─', ' ', ' ', ' ', ' ']
            [' ', ' ', '├', '─', ' ', ' ', ' ']
            [' ', ' ', '└', '─', ' ', ' ', ' ']
            [' ', ' ', ' ', '├', '─', ' ', ' ']
            [' ', ' ', ' ', '└', '─', ' ', ' ']
            [' ', '└', '─', ' ', ' ', ' ', ' ']
        """
        beads_of_prefixes = [self.space] * (len(visibility_mask)
                                            + JUST_IN_CASE)

        if depth:
            if node.number == node.total_relatives():
                beads_of_prefixes[depth] = self.edge
                visibility_mask[depth] = 0

            else:
                beads_of_prefixes[depth] = self.section
                visibility_mask[depth] = 1

            beads_of_prefixes[depth + 1] = self.line
        return beads_of_prefixes

    def apply_mask(self, beads_of_prefixes: List[str],
                   visibility_mask: List[int]) -> None:
        """Наложить маску на бусины.

        Мы ищем вертикальные куски, где должны быть линии и добавляем их,
        до тех пор, пока не увидим терминальный символ
        (обычно угол, поворачивающий к ноде.)

[' ', '├', '─', ' ', ' ', ' ', ' ']   -->   [' ', '├', '─', ' ', ' ', ' ', ' ']
[' ', ' ', '├', '─', ' ', ' ', ' ']   -->   [' ', '│', '├', '─', ' ', ' ', ' ']
[' ', ' ', '└', '─', ' ', ' ', ' ']   -->   [' ', '│', '└', '─', ' ', ' ', ' ']
[' ', ' ', ' ', '├', '─', ' ', ' ']   -->   [' ', '│', ' ', '├', '─', ' ', ' ']
[' ', ' ', ' ', '└', '─', ' ', ' ']   -->   [' ', '│', ' ', '└', '─', ' ', ' ']
[' ', '└', '─', ' ', ' ', ' ', ' ']   -->   [' ', '└', '─', ' ', ' ', ' ', ' ']
        """
        for i, line in enumerate(visibility_mask):
            if line:
                if beads_of_prefixes[i] != self.section:
                    beads_of_prefixes[i] = self.vert

    def apply_spacing(self, beads_of_prefixes: List[str]) -> None:
        """Начинаем считать справа налево и, до тех пор
        пока не упрёмся в символ, заполняем пробелы специальным знаком.
        Потом там будет широкий пробел.

[' ', '├', '─', ' ', ' ', ' ', ' ']   -->   [' ', '├', '─', '#', '#', '#', '#']
[' ', '│', '├', '─', ' ', ' ', ' ']   -->   [' ', '│', '├', '─', '#', '#', '#']
[' ', '│', '└', '─', ' ', ' ', ' ']   -->   [' ', '│', '└', '─', '#', '#', '#']
[' ', '│', ' ', '├', '─', ' ', ' ']   -->   [' ', '│', ' ', '├', '─', '#', '#']
[' ', '│', ' ', '└', '─', ' ', ' ']   -->   [' ', '│', ' ', '└', '─', '#', '#']
[' ', '└', '─', ' ', ' ', ' ', ' ']   -->   [' ', '└', '─', '#', '#', '#', '#']
        """
        for i in range(len(beads_of_prefixes) - 1, -1, -1):
            if beads_of_prefixes[i] == self.space:
                beads_of_prefixes[i] = '#'
            else:
                break

    def format_spacer(self, beads_of_prefixes: List[str]) -> str:
        """Преобразовать бусины в настоящие строки-заполнители.

        Заменяем пробелы на широкие заполнители. Кроме корневой ноды.
        [' ', ' ', ' ', ' ', ' ', ' ', ' ']   -->   ''
        [' ', '├', '─', '#', '#', '#', '#']   -->   '        ├─'
        [' ', '│', '├', '─', '#', '#', '#']   -->   '        │     ├─'
        [' ', '│', '└', '─', '#', '#', '#']   -->   '        │     └─'
        [' ', '│', ' ', '├', '─', '#', '#']   -->   '        │           ├─'
        [' ', '│', ' ', '└', '─', '#', '#']   -->   '        │           └─'
        [' ', '└', '─', '#', '#', '#', '#']   -->   '        └─'
        """
        if all(x == self.space for x in beads_of_prefixes):
            return ''

        string_spacer = ''
        for letter in beads_of_prefixes:
            if letter == self.vert:
                string_spacer += '{elem:^{width}}'.format(
                    elem=self.vert,
                    width=self.space_blocks
                )

            elif letter == self.line:
                string_spacer += self.line * self.line_blocks

            elif letter in (self.edge, self.section):
                string_spacer += self.space \
                                 * (self.space_blocks // 2 - 1) + letter

            elif letter == self.section:
                string_spacer += self.section

            elif letter != '#':
                string_spacer += self.space * self.space_blocks

        return string_spacer

    def describe(self, node) -> str:
        """Превратить дерево в текстовый вид.

        На выходе должно получиться что-то такое:

        BinOpNode-59234264 (Plus)
                ├─────BinOpNode-59234240 (Plus)
                │     ├─────VariableNode-59234288 (value=1)
                │     └─────BinOpNode-59234336 (Multiply)
                │           ├─────VariableNode-59234384 (value=2)
                │           └─────VariableNode-59234432 (value=3)
                └─────VariableNode-59234504 (value=1)
        """
        output = ''
        children = list(node.iter_recursively(depth=0))
        total = len(children)
        visibility_mask = [0] * total

        for child, depth in children:
            beads_of_prefixes = self.form_beads(visibility_mask, child, depth)

            if depth:
                self.apply_mask(beads_of_prefixes, visibility_mask)
                self.apply_spacing(beads_of_prefixes)

            string_spacer = self.format_spacer(beads_of_prefixes)
            output += '\n' + self.output_head(string_spacer, child)

        return output.strip()

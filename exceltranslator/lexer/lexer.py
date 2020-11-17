# -*- coding: utf-8 -*-

"""Лексический анализатор.
"""
from collections import deque
from typing import Type, Tuple, List, NoReturn, Deque, Optional

from exceltranslator import settings
from exceltranslator.exceptions import CustomSyntaxError
from exceltranslator.lexer.base_tokens import BaseToken
from exceltranslator.lexer.tokens import known_tokens

__all__ = [
    'BaseLexer',
    'Lexer',
]


class BaseLexer:
    """Лексический анализатор.
    """
    digits = set('0123456789')
    letters = set(r"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                  r"abcdefghijklmnopqrstuvwxyz"
                  r"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
                  r"абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    punctuation = set(r"""+-*/\=,()[]{};"'!?.:№%<>@_ """ + '\n\t\r')
    white_list = set.union(digits, letters, punctuation)
    # ширина отображаемого кода при обнаружении ошибки
    display_window: int = 10

    def __init__(self):
        """Инициализировать экземпляр.
        """
        self.source_code = ''
        self.preprocessed_code = ''
        self.tokens: Tuple[BaseToken, ...] = ()
        self._runtime_tokens: Deque[BaseToken] = deque()

    def clear(self) -> None:
        """Сбросить параметры до исходных, кроме известных токенов.
        """
        self.source_code = ''
        self.preprocessed_code = ''
        self._runtime_tokens = deque(self.tokens)

    def error(self, description: str) -> NoReturn:
        """Выдать синтаксическую ошибку.
        """
        raise CustomSyntaxError(f'Синтаксическая ошибка: {description}')

    def register(self, *token_types: Type[BaseToken]) -> None:
        """Зарегистрировать токены в лексере.
        """
        self.tokens = tuple(token_types)

    def check_quotes(self, input_text: str) -> None:
        """Убедиться, что кавычки в тексте расставлены правильно.
        """
        single_amount = 0
        double_amount = 0
        single_last_seen = 0
        double_last_seen = 0

        for i, symbol in enumerate(input_text, start=1):
            if symbol == "'":
                single_amount += 1
                single_last_seen = i

            elif symbol == '"':
                double_amount += 1
                double_last_seen = i

        if single_amount and single_amount % 2:
            source = self.problem_at(single_last_seen - 1, input_text)
            self.error(f"нечётное число одинарных кавычек. "
                       f"Последняя из них символ №{single_last_seen} {source}")

        if double_amount and double_amount % 2:
            source = self.problem_at(double_last_seen - 1, input_text)
            self.error(f"нечётное число двойных кавычек. "
                       f"Последняя из них символ №{double_last_seen} {source}")

    def check_parenthesis(self, input_text: str) -> None:
        """Убедиться, что скобки в тексте расставлены правильно.
        """
        open_normal = '('
        close_normal = ')'

        open_brace = '['
        close_brace = ']'

        open_curly = '{'
        close_curly = '}'

        open_types = {open_normal, open_brace, open_curly}
        close_types = {close_brace, close_curly, close_normal}
        stack = deque()
        artifact = ''
        index = 0

        for i, symbol in enumerate(input_text):
            index = i
            artifact = symbol

            if symbol in open_types:
                stack.append(symbol)

            elif symbol in close_types:
                last_open = stack.pop() if stack else None

                if (
                        (symbol == close_normal and last_open != open_normal)
                        or (symbol == close_brace and last_open != open_brace)
                        or (symbol == close_curly and last_open != open_curly)
                ):
                    break
                else:
                    artifact = ''

            else:
                artifact = ''

        if not artifact and not stack:
            return None

        message = (
            'символ "{symbol}" (№{number}) не имеет пары. {source}'.format(
                symbol=artifact,
                number=index + 1,
                source=self.problem_at(index, input_text))
        )
        self.error(message)

    def problem_at(self, index: int, input_text: str) -> str:
        """Оформить отображения места, вызвавшего ошибку.
        """
        left = index - self.display_window
        if left < 0:
            left = 0
            prefix = ''
        else:
            prefix = '...'

        right = index + self.display_window
        if right <= len(input_text):
            suffix = '...'
        else:
            suffix = ''

        source = prefix + (input_text[left:index]
                           + ' --> ' + input_text[index] + ' <-- '
                           + input_text[index + 1:right]) + suffix
        return source

    def preprocess(self, input_text: str) -> str:
        """Предварительная обработка.
        """
        if delta := set(input_text) - self.white_list:
            self.error(
                'в скрипте нельзя использовать символы {}'.format(
                    ''.join(repr(x) for x in sorted(delta))
                )
            )

        self.check_parenthesis(input_text)
        self.check_quotes(input_text)

        return input_text

    def tokenize(self, input_text: str) -> List[BaseToken]:
        """Разложить текст на токены.
        """
        # FIXME - очень неоптимальная реализация!
        string = input_text
        output: List[BaseToken] = []
        position = 0

        while position < len(string):
            while string[position] in ('\n', '\t', ' ', '\r'):
                position += 1
                if position >= len(string):
                    break

            for token_type in self.tokens:
                token, end = token_type.try_making(string[position:])

                if token is not None:
                    position += end
                    output.append(token)
                    break

                if position >= len(string):
                    break

            else:
                raise ValueError(
                    f'Не удалось распознать символ: {string[0]!r}'
                )

        return output

    @property
    def tokens_left(self) -> List[str]:
        """Отобразить, какие токены осталось обработать.
        """
        return [str(x) for x in self._runtime_tokens]

    def analyze(self, source_code: str) -> None:
        """Разложить исходный код на набор токенов.
        """
        if (size := len(source_code)) > settings.MAX_LETTERS:
            self.error(f'Слишком длинный текст: {size} символов.')

        self.clear()
        self.source_code = source_code
        self.preprocessed_code = self.preprocess(self.source_code)
        self._runtime_tokens = deque(self.tokenize(self.preprocessed_code))

    def cut_next(self):
        """Откусить следующий символ от последовательности.
        """
        next_one = None
        if self._runtime_tokens:
            next_one = self._runtime_tokens.popleft()
        return next_one

    def dispose_next(self, token_type: Type) -> None:
        """Удалить токен по причине ненужности.
        """
        next_one = self.cut_next()

        if not isinstance(next_one, token_type):
            self.error(
                f'Предполагалось уничтожить токен типа {token_type.__name__},'
                f' а уничтожается {type(next_one).__name__}.'
            )

    def show_next(self) -> Optional[BaseToken]:
        """Показать следующий символ (не откусывая его).
        """
        next_one = None
        if self._runtime_tokens:
            next_one = self._runtime_tokens[0]
        return next_one

    def next_in(self, *args) -> bool:
        """Проверить, входит ли следующий символ в эти типы.
        """
        return type(self.show_next()) in args


class Lexer(BaseLexer):
    """Лексер как базовый, но автоматически регистрирует все известные токены.
    """

    def __init__(self):
        """Инициализировать экземпляр.
        """
        super().__init__()
        self.register(*known_tokens)

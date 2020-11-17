# -*- coding: utf-8 -*-

"""Парсер синтаксического дерева.
"""
from typing import Type, List

from exceltranslator.exceptions import CustomSyntaxError
from exceltranslator.lexer.base_tokens import LiteralToken, NumberToken
from exceltranslator.lexer.lexer import Lexer
from exceltranslator.lexer.tokens import *
from exceltranslator.parser.base_nodes import *
from exceltranslator.parser.nodes import *


class Parser:
    """Парсер синтаксического дерева.
    """

    def __init__(self, lexer: Lexer):
        """Инициализировать экземпляр.
        """
        self.lexer = lexer

    def parse(self):
        """Собрать синтаксическое дерево из кода.
        """
        root = self.tier_8(depth=0)
        return root

    def tier_8(self, depth: int) -> BaseNode:
        """Приоритет 8. Инструкции.
        """
        head = InstructionNode()

        while self.lexer.tokens_left:
            new_node = self.tier_7(depth=depth + 1)

            if type(new_node) != StopNode:
                head.add_nodes(new_node)

            if self.lexer.next_in(RightCur):
                break

        return head

    def tier_7(self, depth: int) -> BaseNode:
        """Приоритет 7. Присваивание.
        """
        head = self.tier_6(depth=depth + 1)

        while self.lexer.next_in(Assignment) and not type(head) == StopNode:
            head = AssigmentNode(left_operand=head,
                                 operator=self.lexer.cut_next(),
                                 right_operand=self.tier_6(depth=depth + 1))
        return head

    def tier_6(self, depth: int) -> BaseNode:
        """Приоритет 6. Логические операции.
        """
        head = self.tier_5(depth=depth + 1)

        while self.lexer.next_in(AndToken, OrToken) \
                and not type(head) == StopNode:
            head = LogicalNode(left_operand=head,
                               operator=self.lexer.cut_next(),
                               right_operand=self.tier_5(depth=depth + 1))
        return head

    def tier_5(self, depth: int) -> BaseNode:
        """Приоритет 5. Равно и не равно.
        """
        head = self.tier_4(depth=depth + 1)

        while self.lexer.next_in(EqualToken, NotEqualToken) \
                and not type(head) == StopNode:
            head = LogicalNode(left_operand=head,
                               operator=self.lexer.cut_next(),
                               right_operand=self.tier_4(depth=depth + 1))
        return head

    def tier_4(self, depth: int) -> BaseNode:
        """Приоритет 4. Больше, меньше.
        """
        head = self.tier_3(depth=depth + 1)

        while self.lexer.next_in(GT, LT, LE, GE) \
                and not type(head) == StopNode:
            head = LogicalNode(left_operand=head,
                               operator=self.lexer.cut_next(),
                               right_operand=self.tier_3(depth=depth + 1))
        return head

    def tier_3(self, depth: int) -> BaseNode:
        """Приоритет 3. Сложение и вычитание.
        """
        head = self.tier_2(depth=depth + 1)

        while self.lexer.next_in(Plus, Minus) and not type(head) == StopNode:
            head = BinaryNode(left_operand=head,
                              operator=self.lexer.cut_next(),
                              right_operand=self.tier_2(depth=depth + 1))
        return head

    def tier_2(self, depth: int) -> BaseNode:
        """Приоритет 2. Умножение и деление.
        """
        head = self.tier_1(depth=depth + 1)

        while self.lexer.next_in(Multiply, Divide) \
                and not type(head) == StopNode:
            head = BinaryNode(left_operand=head,
                              operator=self.lexer.cut_next(),
                              right_operand=self.tier_1(depth=depth + 1))
        return head

    def tier_1(self, depth: int) -> BaseNode:
        """Приоритет 1. Возведение в степень.
        """
        head = self.tier_0(depth=depth + 1)

        while self.lexer.next_in(PowerToken) and not type(head) == StopNode:
            head = BinaryNode(left_operand=head,
                              operator=self.lexer.cut_next(),
                              right_operand=self.tier_0(depth=depth + 1))
        return head

    def tier_0(self, depth: int) -> BaseNode:
        """Приоритет 0. Унарный минус и скобки.
        """
        current = self.lexer.cut_next()

        if type(current) == Semicolon:
            return StopNode()

        if isinstance(current, LiteralToken):
            new_node = VarNode(value=current)

        elif type(current) == LeftPar:
            new_node = ParNode(self.tier_7(depth=depth + 1))
            self.lexer.dispose_next(RightPar)

        elif type(current) == Minus \
                and isinstance(self.lexer.show_next(), NumberToken):
            value = VarNode(value=self.lexer.cut_next())
            new_node = UnaryMinusNode(value)

        elif type(current) == NameToken:
            new_node = NameNode(value=current)
            if self.lexer.next_in(LeftPar):
                new_node = self.call_handler(new_node, depth=depth + 1)

        elif type(current) == NotToken:
            new_node = UnaryNotNode(self.tier_1(depth=depth + 1))

        elif type(current) == IfToken:
            new_node = self.if_handler(depth=depth + 1)

        elif type(current) == RightPar:
            new_node = StopNode()

        else:
            raise CustomSyntaxError(
                f'Не удалось обработать токен: {current}, {type(current)}'
            )

        return new_node

    def call_handler(self, name: NameNode, depth: int) -> BaseNode:
        """Функция для обработки аргументов вызова.
        """
        new_node = CallNode(name)

        pars = 0
        while self.lexer.tokens_left:
            if self.lexer.next_in(LeftPar):
                self.lexer.dispose_next(LeftPar)
                pars += 1

            new_argument = self.tier_7(depth=depth + 1)

            if type(new_argument) == StopNode:
                break

            new_node.add_nodes(new_argument)

            if self.lexer.next_in(RightPar):
                self.lexer.dispose_next(RightPar)
                if pars == 1:
                    break
                else:
                    pars -= 1

            if self.lexer.next_in(CommaToken):
                self.lexer.dispose_next(CommaToken)
                continue

        return new_node

    def if_handler(self, depth: int) -> BaseNode:
        """Функция для обработки условий.
        """
        node = ConditionNode()
        cond_if = IfNode()
        node.add_nodes(cond_if)

        self.cut_and_append(cond_if, depth, dispose_types=[LeftPar,
                                                           RightPar])
        self.cut_and_append(cond_if, depth, node_type=ScopeNode)

        while self.lexer.next_in(ElifToken):
            self.lexer.dispose_next(ElifToken)
            cond_elif = ElifNode()

            self.cut_and_append(cond_elif, depth, dispose_types=[LeftPar,
                                                                 RightPar])
            self.cut_and_append(cond_elif, depth, node_type=ScopeNode)
            node.add_nodes(cond_elif)

        if self.lexer.next_in(ElseToken):
            self.lexer.dispose_next(ElseToken)
            cond_else = ElseNode()

            self.cut_and_append(cond_else, depth, node_type=ScopeNode)
            node.add_nodes(cond_else)

        return node

    def cut_and_append(self, head: BaseNode, depth: int,
                       dispose_types: List[Type] = None,
                       node_type: type = None) -> None:
        """Вырезать кусок, подходящий под фрагмент условия.
        """
        if dispose_types is None:
            dispose_types = [LeftCur, RightCur]

        self.lexer.dispose_next(dispose_types.pop(0))

        if node_type is None:
            child = self.tier_7(depth=depth + 1)
        else:
            child = node_type(self.tier_8(depth=depth + 1))

        head.add_nodes(child)

        # TODO
        # while self.lexer.next_in(Semicolon):
        #     self.lexer.dispose_next(Semicolon)

        self.lexer.dispose_next(dispose_types.pop(0))

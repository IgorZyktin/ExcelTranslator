# -*- coding: utf-8 -*-

"""Готовые инструменты.
"""
import time
from typing import Any

from exceltranslator.helpers.namespace_wrapper import (
    NamespaceWrapper,
    Namespace,
)
from exceltranslator.helpers.node_creation_printer import NodeCreationPrinter
from exceltranslator.helpers.node_tree_printer import NodeTreePrinter
from exceltranslator.helpers.stack_wrapper import StackWrapper
from exceltranslator.helpers.watcher import Watcher
from exceltranslator.lexer.lexer import Lexer
from exceltranslator.parser.parser import Parser


def custom_eval(input_text: str, namespace: NamespaceWrapper = None) -> Any:
    """Исполнить код и вернуть результат.
    """
    lexer = Lexer()
    parser = Parser(lexer)
    lexer.analyze(input_text)
    root = parser.parse()

    if namespace is None:
        namespace = Namespace()

    result = root.evaluate(namespace)
    return result


def verbose_eval(input_text: str, colored: bool = True,
                 namespace: NamespaceWrapper = None):
    """Исполнить код и собрать максимум данных о нём.
    """
    report = {}

    lexer = Lexer()
    parser = Parser(lexer)
    parser = NodeCreationPrinter(parser, colored=colored)

    # -----
    start = time.perf_counter()
    lexer.analyze(input_text)
    report['lexical_analysis'] = time.perf_counter() - start
    # -----

    watcher = Watcher()
    node_tree_printer = NodeTreePrinter(colored=colored)
    # -----
    start = time.perf_counter()
    root = parser.parse()
    report['tree_creation'] = time.perf_counter() - start
    # -----

    root.watcher = watcher
    stack = StackWrapper(watcher=watcher)
    if namespace is None:
        namespace = Namespace(watcher=watcher)
    else:
        namespace.watcher = watcher

    # -----
    start = time.perf_counter()
    result = root.evaluate(namespace, stack)
    report['evaluation'] = time.perf_counter() - start
    # -----

    report['tree'] = node_tree_printer.describe(root)
    report['call_stack'] = parser.format_call_stack()
    report['stats'] = watcher.make_report()

    return result, report

# -*- coding: utf-8 -*-

"""Демонстрация работы.
"""
import time

from colorama import init, Fore

from exceltranslator.helpers.namespace_wrapper import Namespace
from exceltranslator.helpers.node_creation_printer import NodeCreationPrinter
from exceltranslator.helpers.node_tree_printer import NodeTreePrinter
from exceltranslator.helpers.stack_wrapper import StackWrapper
from exceltranslator.helpers.watcher import Watcher
from exceltranslator.lexer.lexer import Lexer
from exceltranslator.parser.parser import Parser
from exceltranslator.parser.serialization import serialize_to_python

init(autoreset=True)


def main():
    """Точка входа.
    """
    lexer = Lexer()
    parser = Parser(lexer)
    node_tree_printer = NodeTreePrinter()
    watcher = Watcher()

    source_code = """
    num = СЛЧИС() * 10;
    ЕСЛИ (num >= 9)
    {
        x = ">= 9";
    }
    ИНАЧЕ_ЕСЛИ (num >= 8) 
    {
        x = ">= 8";
    } 
    ИНАЧЕ_ЕСЛИ (num >= 7) 
    {
        x = ">= 7";
    } 
    ИНАЧЕ_ЕСЛИ (num >= 6) 
    {
        x = ">= 6";
    } 
    ИНАЧЕ_ЕСЛИ (num >= 5) 
    {
        x = ">= 5";
    } 
    ИНАЧЕ_ЕСЛИ (num >= 4) 
    {
        x = ">= 4";
    } 
    ИНАЧЕ_ЕСЛИ (num >= 3) 
    {
        x = ">= 3";
    } 
    ИНАЧЕ_ЕСЛИ (num >= 2) 
    {
        x = ">= 2";
    } 
    ИНАЧЕ 
    {
        x = "около 1";
    };
    """

    start = time.perf_counter()
    lexer.analyze(source_code)
    lexical_analysis = time.perf_counter() - start

    start = time.perf_counter()
    parser = NodeCreationPrinter.apply(parser)
    root = parser.parse()
    tree_building = time.perf_counter() - start

    print('-' * 100)
    print(f'Исходный код команды:')
    print(Fore.GREEN + source_code)
    print('-' * 100)

    root.watcher = watcher
    stack = StackWrapper(watcher=watcher)
    namespace = Namespace(watcher=watcher)
    root.evaluate(namespace, stack)

    node_tree_printer(root)
    print('-' * 100)
    print('Полученный в итоге python код:')
    print(Fore.RED + serialize_to_python(root))

    start = time.perf_counter()
    _ = root.evaluate(namespace)
    evaluation = time.perf_counter() - start

    print('-' * 100)
    print(f'На лексический анализ: {lexical_analysis:0.5f} сек.')
    print(f'     На сборку дерева: {tree_building:0.5f} сек.')
    print(f'        На исполнение: {evaluation:0.5f} сек.')
    print()
    print('Результат исполнения кода:')
    print('\tnum -->', namespace['num'])
    print('\t  x -->', namespace['x'])


if __name__ == '__main__':
    main()

"""Точка входа для обратной совместимости: python main.py --address "..." """
import sys

from eda_parser.cli import main

if __name__ == "__main__":
    sys.exit(main())

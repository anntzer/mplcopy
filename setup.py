import ast
import tokenize

from setuptools import setup


setup(
    long_description=ast.get_docstring(
        ast.parse(tokenize.open("src/mplcopy.py").read())),
)

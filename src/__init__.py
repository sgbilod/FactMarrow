"""FactMarrow - Multi-Agent Analysis of Public Health Documents"""

# Python 3.13 compatibility patch for pydantic
import sys
if sys.version_info >= (3, 13):
    import typing
    original_evaluate = typing.ForwardRef._evaluate

    def new_evaluate(self, globalns, localns, type_params=(),
                     recursive_guard=frozenset()):
        return original_evaluate(
            self, globalns, localns, type_params,
            recursive_guard=recursive_guard
        )

    typing.ForwardRef._evaluate = new_evaluate

__version__ = "0.1.0-alpha"
__author__ = "FactMarrow Contributors"


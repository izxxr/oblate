# MIT License

# Copyright (c) 2023 Izhar Ahmad

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from typing import Callable, Any, TypeVar, Tuple, TYPE_CHECKING
from oblate.utils import MISSING

if TYPE_CHECKING:
    from oblate.fields.base import Field
    from oblate.contexts import ErrorFormatterContext

    FT = TypeVar('FT', bound='Field[Any, Any]')
    ErrorFormatterT = Callable[[FT, ErrorFormatterContext], Any]

__all__ = (
    'FIELD_REQUIRED',
    'VALIDATION_FAILED',
    'NONE_DISALLOWED',
    'INVALID_DATATYPE',
    'NONCONVERTABLE_VALUE',
    'DISALLOWED_FIELD',
)

_index = 0
_error_codes = []

def _errcode(alias: bool = False) -> int:
    global _index, _error_codes
    value = 1 << _index

    if not alias:
        _index += 1
        _error_codes.append(value)

    return value


def error_formatter(*error_codes: int) -> Callable[[ErrorFormatterT[FT]], ErrorFormatterT[FT]]:
    """A decorator to register an error formatter.

    An error formatter is used to customize standard error messages. The
    decorated function must take two arguments: self and the error formatter
    context instance.

    Parameters
    ----------
    *error_codes: :class:`int`
        The error codes that can be handled by this formatter.
    """
    def __wrapper(func: ErrorFormatterT) -> ErrorFormatterT:
        # An internal hack to register error formatter for all errors
        # NOTE: UNDOCUMENTED AND ONLY FOR INTERNAL USE!
        nonlocal error_codes
        if error_codes and error_codes[0] is MISSING:
            error_codes = tuple(_error_codes)

        func.__oblate_error_formatter_codes__ = error_codes
        return func
    return __wrapper

# Basic validation errors
FIELD_REQUIRED = _errcode()
VALIDATION_FAILED  = _errcode()
NONE_DISALLOWED = _errcode()

# General field errors
INVALID_DATATYPE = _errcode()
NONCONVERTABLE_VALUE = _errcode()

# Nested field errors
DISALLOWED_FIELD = _errcode()

# TODO: This error is not bound to a field and currently there is no support
# for non-field errors. The below line should be uncommented when the
# support is implemented for non-field errors.
# UNKNOWN_FIELD = _errcode()

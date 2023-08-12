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

from typing import Any
from oblate.utils import MISSING

__all__ = (
    'ErrorFormatterContext',
)

class ErrorFormatterContext:
    """The error formatter context.

    This class holds important information that is passed to an error
    formatter. It should not be initialized manually.

    Attributes
    ----------
    error_code: :class:`int`
        The :ref:`error code <tut-errors-handling-error-codes>` used to
        determine the type of error.
    """
    __slots__ = (
        'error_code',
        '_value',
    )

    def __init__(
            self,
            *,
            error_code: int,
            value: Any = MISSING,
        ):

        self.error_code = error_code
        self._value = value

    def get_value(self) -> Any:
        """Gets the value that caused the error.

        .. note::

            For some error codes, there is no value associated to the error. In
            those cases, a ValueError is raised indicating that the error has
            no value associated.
        """
        value = self._value
        if value is MISSING:
            raise ValueError('This error has no value')
        
        return value

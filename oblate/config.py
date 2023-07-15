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

"""Manage global Oblate configuration."""

from __future__ import annotations

from typing import Type
from types import SimpleNamespace
from oblate.exceptions import SchemaValidationFailed

__all__ = (
    'set_validation_fail_exception',
    'get_validation_fail_exception',
)

_glob_config = SimpleNamespace(validation_fail_exception=SchemaValidationFailed)

def set_validation_fail_exception(exc: Type[SchemaValidationFailed], /) -> None:
    """Sets the exception to raise instead of :exc:`SchemaValidationFailed`.

    Parameters
    ----------
    exc: Type[:exc:`SchemaValidationFailed`]
        The subclass of :exc:`SchemaValidationFailed` to raise on validation
        failure.
    """
    if not issubclass(exc, SchemaValidationFailed):
        raise TypeError('First argument in set_validation_fail_exception() must be a subclass of SchemaValidationFailed')

    _glob_config.validation_fail_exception = exc

def get_validation_fail_exception() -> Type[SchemaValidationFailed]:
    """Gets the current exception raised on schema validation failure.

    Returns
    -------
    Type[:exc:`SchemaValidationFailed`]
        The resolved value.
    """
    return _glob_config.validation_fail_exception
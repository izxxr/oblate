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

from typing import TYPE_CHECKING, Any
from contextvars import ContextVar

if TYPE_CHECKING:
    from oblate.contexts import _BaseValueContext
    from oblate.schema import Schema

__all__ = (
    'MissingType',
    'MISSING',
    'current_context',
    'current_field_key',
)


class MissingType:
    """Type for representing unaltered/default/missing values.

    Used as sentinel to differentiate between default and None values.
    utils.MISSING is a type safe instance of this class.
    """
    def __repr__(self) -> str:
        return '...'  # pragma: no cover

    def __bool__(self) -> bool:
        return False  # pragma: no cover


MISSING: Any = MissingType()


### Context variables ###

current_context: ContextVar[_BaseValueContext] = ContextVar('_current_context')
current_field_key: ContextVar[str] = ContextVar('current_field_key')
current_schema: ContextVar[Schema] = ContextVar('current_schema')

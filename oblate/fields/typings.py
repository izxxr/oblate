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

from oblate.fields.base import Field

# typing imported as t to avoid name conflict with classes
# defined in this module
import typing as t

if t.TYPE_CHECKING:  # pragma: no cover
    from oblate.contexts import LoadContext, DumpContext, ErrorContext
    from oblate.exceptions import FieldError

__all__ = (
    'Any',
    'Literal',
)

_T = t.TypeVar('_T')


class Any(Field[t.Any, t.Any]):
    """A field that accepts any arbitrary value.

    This field acts as a "raw field" that performs no validation on the
    given value.
    """
    __slots__ = ()

    def value_load(self, value: Any, context: LoadContext) -> Any:
        return value

    def value_dump(self, value: Any, context: DumpContext) -> Any:
        return value


class Literal(Field[_T, _T]):
    """A field that accepts only exact literal values.

    This works in a similar fashion as :class:`typing.Literal`.

    Parameters
    ----------
    *values:
        The literal values.
    """
    __slots__ = ('_values', '_msg')

    ERR_INVALID_VALUE = 'literal.invalid_value'

    def __init__(self, *values: _T, **kwargs: t.Any) -> None:
        self._values = values
        self._msg = f'Value must be one of: {", ".join(repr(value) for value in self._values)}'
        super().__init__(**kwargs)

    def format_error(self, error_code: t.Any, context: ErrorContext) -> t.Union[FieldError, str]:
        if error_code == self.ERR_INVALID_VALUE:
            return self._msg

        return super().format_error(error_code, context)  # pragma: no cover

    def value_load(self, value: t.Any, context: LoadContext) -> _T:
        if value not in self._values:
            raise self._call_format_error(self.ERR_INVALID_VALUE, context.schema, value)

        return value

    def value_dump(self, value: _T, context: DumpContext) -> t.Any:
        return value

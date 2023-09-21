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
from oblate.exceptions import FieldError
from oblate import utils

# typing imported as t to avoid name conflict with classes
# defined in this module
import typing as t

if t.TYPE_CHECKING:  # pragma: no cover
    from oblate.contexts import LoadContext, DumpContext, ErrorContext

__all__ = (
    'Any',
    'Literal',
    'Union',
    'TypeExpr',
)

_T = t.TypeVar('_T')


class Any(Field[t.Any, t.Any]):
    """A field that accepts any arbitrary value.

    This field acts as a "raw field" that performs no validation on the
    given value.
    """
    def value_load(self, value: Any, context: LoadContext) -> Any:
        return value

    def value_dump(self, value: Any, context: DumpContext) -> Any:
        return value


class Literal(Field[_T, _T]):
    """A field that accepts only exact literal values.

    This works in a similar fashion as :class:`typing.Literal`.

    .. versionadded:: 1.1

    Attributes
    ----------
    ERR_INVALID_VALUE:
        Error raised when the given value is not from the provided literal value.

    Parameters
    ----------
    *values:
        The literal values.
    """
    ERR_INVALID_VALUE = 'literal.invalid_value'

    def __init__(self, *values: _T, **kwargs: t.Any) -> None:
        self.values = values
        self._tp = utils.TypeValidator(t.Literal[*values])  # type: ignore
        super().__init__(**kwargs)

    def _get_default_error_message(self, error_code: t.Any, context: ErrorContext) -> t.Union[FieldError, str]:
        if error_code == self.ERR_INVALID_VALUE:
            return FieldError(context.metadata['type_validation_fail_errors'])

        return super()._get_default_error_message(error_code, context)  # pragma: no cover

    def value_load(self, value: t.Any, context: LoadContext) -> _T:
        validated, errors = self._tp.validate(value)  # type: ignore
        if not validated:
            metadata = {'type_validation_fail_errors': errors}
            raise self._call_format_error(self.ERR_INVALID_VALUE, context.schema, value, metadata)
        return value

    def value_dump(self, value: _T, context: DumpContext) -> t.Any:
        return value


class Union(Field[_T, _T]):
    """A field that accepts values of any of the given data types.

    This is similar to the :class:`typing.Union` type. Note that this field
    only performs simple :func:`isinstance` check on the given value.

    .. versionadded:: 1.1

    Attributes
    ----------
    ERR_INVALID_VALUE:
        Error raised when the given value is not from the provided types.

    Parameters
    ----------
    *types: :class:`type`
        The list of types to accept.
    """
    ERR_INVALID_VALUE = 'union.invalid_value'

    def __init__(self, *types: t.Type[_T], **kwargs: t.Any):
        if len(types) < 2:
            raise TypeError('fields.Union() accepts at least two arguments')  # pragma: no cover

        self.types = types
        self._tp = utils.TypeValidator(t.Union[*types])  # type: ignore
        super().__init__(**kwargs)

    def _get_default_error_message(self, error_code: t.Any, context: ErrorContext) -> t.Union[FieldError, str]:
        if error_code == self.ERR_INVALID_VALUE:
            return FieldError(context.metadata['type_validation_fail_errors'])

        return super()._get_default_error_message(error_code, context)  # pragma: no cover

    def value_load(self, value: t.Any, context: LoadContext) -> _T:
        validated, errors = self._tp.validate(value)  # type: ignore
        if not validated:
            metadata = {'type_validation_fail_errors': errors}
            raise self._call_format_error(self.ERR_INVALID_VALUE, context.schema, value, metadata)
        return value

    def value_dump(self, value: _T, context: DumpContext) -> _T:
        return value


class TypeExpr(Field[_T, _T]):
    """A field that accepts value compatible with given type expression.

    For the list of supported types and limitations of this field, please see
    the :ref:`guide-type-validation` section.

    .. versionadded:: 1.1

    Parameters
    ----------
    expr:
        The type expression that should be used to validate the type of
        given value.
    """
    ERR_TYPE_VALIDATION_FAILED = 'type_expr.type_validation_failed'

    def __init__(self, expr: t.Type[_T], **kwargs: t.Any):
        self.expr = expr
        self._tp = utils.TypeValidator(expr)
        super().__init__(**kwargs)

    def _get_default_error_message(self, error_code: t.Any, context: ErrorContext) -> t.Union[FieldError, str]:
        if error_code == self.ERR_TYPE_VALIDATION_FAILED:
            return FieldError(context.metadata['type_validation_fail_errors'])

        return super()._get_default_error_message(error_code, context)  # pragma: no cover

    def value_load(self, value: t.Any, context: LoadContext) -> _T:
        validated, errors = self._tp.validate(value)
        if not validated:
            metadata = {'type_validation_fail_errors': errors}
            raise self._call_format_error(self.ERR_TYPE_VALIDATION_FAILED, context.schema, value, metadata)
        return value

    def value_dump(self, value: _T, context: DumpContext) -> _T:
        return value

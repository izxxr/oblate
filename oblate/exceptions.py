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

from typing import TYPE_CHECKING, Any, Optional, List, Dict, Union
from oblate.utils import current_field_name, current_context, current_schema

if TYPE_CHECKING:
    from oblate.fields.base import Field

__all__ = (
    'OblateException',
    'FieldError',
    'ValidationError'
)


class OblateException(Exception):
    """Base class for all exceptions provided by Oblate."""


class FieldError(OblateException):
    """An error raised when validation fails for a field.

    This error when raised in validators or other user-side code is accounted
    as validation error and is included in the subsequent raised :exc:`ValidationError`.

    For convenience, instead of raising this error directly, you should raise :exc:`ValueError`
    or :exc:`AssertionError` in your validators code which would automatically be wrapped
    as a field error.

    Parameters
    ----------
    message:
        The error message.
    state:
        The state to attach to this error. This parameter allows users to attach
        extra state that can be accessed later. Library will not be performing any
        manipulations on this value.

    Attributes
    ----------
    context: Optional[Union[:class:`LoadContext`, :class:`DumpContext`]]
        The current context in which the error was raised. Could be None if
        no context exists.
    schema: :class:`Schema`
        The schema that the error originates from.
    """
    __slots__ = (
        'message',
        'state',
        'context',
        '_field_name',
    )

    def __init__(self, message: Any, /, state: Any = None) -> None:
        self.message = message
        self.state = state
        self.context = current_context.get(None)
        self.schema = current_schema.get()
        self._field_name = current_field_name.get()
        super().__init__(message)

    @classmethod
    def _from_standard_error(cls, err: Union[ValueError, AssertionError]) -> FieldError:
        message = str(err)
        if not message:
            message = 'Validation failed for this field.'

        return cls(message)

    @property
    def field(self) -> Optional[Field[Any, Any]]:
        """The :class:`~fields.Field` that caused the error.

        If this returns None, it means that the causative field doesn't
        exist. An example of this case is when an invalid field name is
        passed during schema initialization.

        :type: :class:`fields.Field`
        """
        return self.schema.__fields__.get(self._field_name, None)

    @property
    def field_name(self) -> str:
        """The name of field that caused the error.

        This name might not always point to an existing field. For example,
        if the causative field doesn't exist.

        :type: :class:`str`
        """
        return self._field_name


class ValidationError(OblateException):
    """An error raised when validation fails with one or more :class:`FieldError`.

    Parameters
    ----------
    errors: List[:class:`FieldError`]
        The errors that caused the validation failure.
    schema: :class:`Schema`
        The schema this error originates from.
    """
    def __init__(self, errors: List[FieldError]) -> None:
        self.errors = errors
        self.schema = current_schema.get()
        super().__init__(self._make_message())

    def _make_message(self, field_errors: Optional[Dict[str, List[str]]] = None, level: int = 0) -> str:
        if field_errors is None:
            field_errors = self._raw_std()

        builder: List[str] = []
        if level == 0:
            schema_name = self.schema.__class__.__qualname__
            builder.append(f'│ {len(field_errors)} validation {"errors" if len(field_errors) > 1 else "error"} in schema {schema_name!r}')

        indent = level*4
        for name, errors in field_errors.items():
            builder.append(f'{" "*indent}│')
            builder.append(f'{" "*indent}└── In field {name}:')
            for idx, error in enumerate(errors):
                if isinstance(error, dict):
                    builder.append(self._make_message(error, level=level+1))
                    continue

                prefix = '└──' if idx == len(errors) - 1 else '├──' 
                builder.append(f'{" "*(indent+4)}{prefix} {error}')

        if level != 0:
            return '\n'.join(builder)

        return '\n│\n' + '\n'.join(builder)

    def _raw_std(self) -> Dict[str, List[str]]:
        out: Dict[str, List[str]] = {}
        for error in self.errors:
            if error.field_name in out:
                out[error.field_name].append(error.message)
            else:
                out[error.field_name] = [error.message]

        return out

    def raw(self) -> Any:
        """Converts the error into raw format.

        The standard format returned by this method is a dictionary containing
        field names as keys and list of error messages as the value.

        This method can be overriden to implement a custom format.
        """
        return self._raw_std()

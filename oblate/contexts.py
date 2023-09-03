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

from typing import TYPE_CHECKING, Any, Set, Dict
from oblate.utils import MISSING

if TYPE_CHECKING:
    from oblate.schema import Schema
    from oblate.fields.base import Field

__all__ = (
    'SchemaContext',
    'LoadContext',
    'DumpContext',
    'ErrorContext',
)


class SchemaContext:
    """Context for a schema instance.

    This class holds information about a :class:`Schema` state. The instance of this class
    is accessed by the :attr:`Schema.context` attribute.

    Attributes
    ----------
    schema: :class:`Schema`
        The schema that this context belongs to.
    config: :class:`SchemaConfig`
        The configuration of schema.
    state:
        An attribute to store any state data. This can be used to propagate or store
        important data while working with schema. By default, this is ``None``.

        .. note::

            Use the ``state`` parameter in :class:`Schema` initialization to modify
            the initial value of state.
    """
    __slots__ = (
        'schema',
        'state',
        'config',
        '_initialized'
    )

    def __init__(self, schema: Schema, state: Any = None) -> None:
        self.schema = schema
        self.config = schema.__config__
        self.state = state
        self._initialized = False

    def is_initialized(self) -> bool:
        """Indicates whether the schema has initialized successfully."""
        return self._initialized


class _BaseValueContext:
    __slots__ = (
        '_field',
        'value',
        'schema',
        'state'
    )

    def __init__(
            self,
            *,
            field: Field[Any, Any],
            value: Any,
            schema: Schema,
        ) -> None:

        self._field = field
        self.value = value
        self.schema = schema
        self.state: Dict[str, Any] = {}

    @property
    def field(self) -> Field[Any, Any]:
        return self._field  # type: ignore  # pragma: no cover


class LoadContext(_BaseValueContext):
    """Context for value deserialization.

    This class holds important and useful information regarding deserialization
    of a value. The instance of this class is passed to :meth:`fields.Field.value_load`
    while a field is being serialized.

    Attributes
    ----------
    field: :class:`fields.Field`
        The field that the context belongs to.
    schema: :class:`Schema`
        The schema that the context belongs to.
    value:
        The raw value being deserialized.
    state: Dict[:class:`str`, Any]
        A dictionary to store any state data. This can be used to propagate or store
        important data while working with schema.
    """
    __slots__ = ()

    def is_update(self) -> bool:
        """Indicates whether the value is being updated.

        This is True when value is being updated and False when value is
        being initially set during schema initialization.
        """
        # Update can only occur after schema initialization
        return self.schema._context.is_initialized()


class DumpContext(_BaseValueContext):
    """Context for value serialization.

    This class holds important and useful information regarding serialization
    of a value. The instance of this class is passed to :meth:`fields.Field.value_dump`
    while a field is being deserialized.

    Attributes
    ----------
    field: :class:`fields.Field`
        The field that the context belongs to.
    schema: :class:`Schema`
        The schema that the context belongs to.
    value:
        The value being serialized.
    included_fields: Set[:class:`str`]
        The set of names of fields that are being serialized.
    state: Dict[:class:`str`, Any]
        A dictionary to store any state data. This can be used to propagate or store
        important data while working with schema.
    """
    __slots__ = (
        'included_fields',
    )

    def __init__(
            self,
            included_fields: Set[str],
            **kwargs: Any,
        ):

        self.included_fields = included_fields
        super().__init__(**kwargs)

class ErrorContext:
    """Context for error handling.

    The instance of this class is passed to :meth:`Field.format_error` method
    and holds information about the error.

    Attributes
    ----------
    error_code:
        The error code indicating the error raised.
    field: :class:`fields.Field`
        The field that the error belongs to.
    schema: :class:`Schema`
        The schema that the error was caused from.
    """
    __slots__ = (
        'schema',
        'error_code',
        '_value',
        '_field',
    )

    def __init__(
            self,
            *,
            error_code: Any,
            schema: Schema,
            field: Field[Any, Any],
            value: Any = MISSING,
        ):

        self.error_code = error_code
        self.schema = schema
        self._field = field
        self._value = value

    @property
    def field(self) -> Field[Any, Any]:
        return self._field  # type: ignore  # pragma: no cover

    def get_value(self) -> Any:
        """Returns the value that caused the error.

        This method will raise a :exc:`ValueError` if no value is
        associated to the error. This is only the case for the 
        :attr:`~fields.Field.FIELD_REQUIRED` error code.

        Raises
        ------
        ValueError
            No value associated to the error.
        """
        if self._value is MISSING:
            raise ValueError('No value associated to the error')  # pragma: no cover
        return self._value

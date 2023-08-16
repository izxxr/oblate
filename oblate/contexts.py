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

from typing import TYPE_CHECKING, Any, Set

if TYPE_CHECKING:
    from oblate.schema import Schema
    from oblate.fields.base import Field

__all__ = (
    'SchemaContext',
    'LoadContext',
    'DumpContext',
)


class SchemaContext:
    """Context for a schema instance.

    This class holds information about a :class:`Schema` state. This class is not
    initialized manually. The instance of this class is accessed by the
    :attr:`Schema.context` attribute.

    Attributes
    ----------
    schema: :class:`Schema`
        The schema that this context belongs to.
    """
    __slots__ = (
        'schema',
        '_initialized'
    )

    def __init__(self, schema: Schema) -> None:
        self.schema = schema
        self._initialized = False

    def is_initialized(self) -> bool:
        """Indicates whether the schema has initialized successfully."""
        return self._initialized


class _BaseValueContext:
    __slots__ = (
        'field',
        'value',
        'schema',
    )

    def __init__(
            self,
            *,
            field: Field[Any, Any],
            value: Any,
            schema: Schema,
        ) -> None:

        self.field = field
        self.value = value
        self.schema = schema

class LoadContext(_BaseValueContext):
    """Context for value serialization.

    This class holds important and useful information regarding serialization
    of a value. This class is not initialized manually. The instance of this
    class is passed to :meth:`Field.value_load` by library.

    Attributes
    ----------
    field: :class:`fields.Field`
        The field that the context belongs to.
    schema: :class:`Schema`
        The schema that the context belongs to.
    value:
        The raw value being serialized.
    """
    def is_update(self) -> bool:
        """Indicates whether the value is being updated.

        This is True when value is being updated and False when value is
        being initially set during schema initialization.
        """
        # Update can only occur after schema initialization
        return self.schema._context.is_initialized()


class DumpContext(_BaseValueContext):
    """Context for value deserialization.

    This class holds important and useful information regarding deserialization
    of a value. This class is not initialized manually. The instance of this
    class is passed to :meth:`Field.value_dump` by library.

    Attributes
    ----------
    field: :class:`fields.Field`
        The field that the context belongs to.
    schema: :class:`Schema`
        The schema that the context belongs to.
    value:
        The value being deserialized.
    included_fields: Set[:class:`str`]
        The set of names of fields that are being deserialized.
    """
    def __init__(
            self,
            included_fields: Set[str],
            **kwargs: Any,
        ):

        self.included_fields = included_fields
        super().__init__(**kwargs)

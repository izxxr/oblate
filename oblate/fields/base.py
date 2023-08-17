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

from typing import TYPE_CHECKING, TypeVar, Generic, Any, Type, Literal, Optional, Union, overload
from typing_extensions import Self
from oblate.utils import MISSING, current_field_name, current_schema
from oblate.exceptions import ValidationError

import copy

if TYPE_CHECKING:
    from oblate.schema import Schema
    from oblate.contexts import LoadContext, DumpContext

__all__ = (
    'Field',
)

RawValueT = TypeVar('RawValueT')
SerializedValueT = TypeVar('SerializedValueT')


class Field(Generic[RawValueT, SerializedValueT]):
    """The base class for all fields.

    Parameters
    ----------
    none: :class:`bool`
        Whether this field allows None values to be set.
    required: :class:`bool`
        Whether this field is required.
    default:
        The default value for this field. If this is passed, the field is automatically
        marked as optional i.e ``required`` parameter gets ignored.

        A callable can also be passed in this parameter that returns the default
        value. The callable takes two parameters, that is the current :class:`SchemaContext`
        instance and the current :class:`Field` instance.
    """

    __slots__ = (
        'none',
        'required',
        '_default',
        '_name',
        '_schema',
    )

    def __init__(
            self,
            *,
            none: bool = False,
            required: bool = True,
            default: Any = MISSING,
        ) -> None:

        self.none = none
        self.required = required and (default is MISSING)
        self._default = default
        self._unbind()

    @overload
    def __get__(self, instance: Literal[None], owner: Type[Schema]) -> Self:
        ...

    @overload
    def __get__(self, instance: Schema, owner: Type[Schema]) -> SerializedValueT:
        ...

    def __get__(self, instance: Optional[Schema], owner: Type[Schema]) -> Union[SerializedValueT, Self]:
        if instance is None:
            return self

        return instance.get_value_for(self._name)

    def __set__(self, instance: Schema, value: RawValueT) -> None:
        current_schema.set(instance)
        current_field_name.set(self._name)
        errors = instance._process_field_value(self, value)
        if errors:
            raise ValidationError(errors)

    def _unbind(self) -> None:
        self._name: str = MISSING
        self._schema: Type[Schema] = MISSING

    def _is_bound(self) -> bool:
        return self._name is not MISSING and self._schema is not MISSING

    def _bind(self, name: str, schema: Type[Schema]) -> None:
        if self._is_bound():
            raise RuntimeError(f"Field {schema.__name__}.{name} is already bound to {self._schema.__name__}.{self._name}")

        self._name = name
        self._schema = schema

    @property
    def default(self) -> Any:
        return self._default if self._default is not MISSING else None

    def has_default(self) -> bool:
        """Indicates whether the field has a default value."""
        return self._default is not MISSING

    def copy(self) -> Field[RawValueT, SerializedValueT]:
        """Copies a field.

        This method is useful when you want to reuse fields from other
        schemas. For example::

            class User(oblate.Schema):
                id = fields.Integer(strict=False)
                username = fields.String()

            class Game(oblate.Schema):
                id = User.id.copy()
                name = fields.String()

        Returns
        -------
        :class:`Field`
            The new field.
        """
        field = copy.copy(self)
        field._unbind()
        return field

    def value_load(self, value: RawValueT, context: LoadContext, /) -> SerializedValueT:
        """Serializes a raw value.

        This is an abstract method that must be implemented by subclasses.

        Parameters
        ----------
        value:
            The value to serialize.
        context: :class:`LoadContext`
            The serialization context.

            .. note::

                The :attr:`LoadContext.value` is the value that needs to
                be serialized.

        Returns
        -------
        The serialized value.
        """
        raise NotImplementedError

    def value_dump(self, value: SerializedValueT, context: DumpContext, /) -> RawValueT:
        """Deserializes the value to raw form.

        This is an abstract method that must be implemented by subclasses.

        Parameters
        ----------
        value:
            The value to deserialize.
        context: :class:`DumpContext`
            The deserialization context.

            .. note::

                The :attr:`DumpContext.value` is the value that needs to
                be deserialized.

        Returns
        -------
        The deserialized value.
        """
        raise NotImplementedError

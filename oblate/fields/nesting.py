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

from typing import TYPE_CHECKING, Mapping, Any, Type, Sequence, Set
from oblate.fields.base import Field, SchemaT
from oblate.exceptions import ValidationError, SchemaValidationFailed
from oblate.utils import MISSING

import collections.abc

if TYPE_CHECKING:
    from oblate.schema import Schema

__all__ = (
    'Object',
    'Partial',
)


class Object(Field[Mapping[str, Any], SchemaT]):
    """Field that allows nesting of schemas.

    Parameters
    ----------
    schema_tp: Type[:class:`Schema`]
        The schema to represent in this field.
    """
    __slots__ = (
        '_schema_tp',
    )

    def __init__(self, schema_tp: Type[SchemaT], **kwargs: Any) -> None:
        self._schema_tp = schema_tp
        super().__init__(**kwargs)

    def value_set(self, value: Any, init: bool) -> SchemaT:
        if isinstance(value, collections.abc.Mapping):
            return self.value_load(value)
        if isinstance(value, self._schema_tp):
            return value
        else:
            raise ValidationError(f'Value for this field must be a {self._schema_tp.__qualname__} object.')

    def value_load(self, value: Mapping[str, Any]) -> SchemaT:
        try:
            return self._schema_tp._from_nested_object(value)
        except SchemaValidationFailed as err:
            raise ValidationError(err.raw()) from None

    def value_dump(self, value: Schema) -> Mapping[str, Any]:
        return value.dump()


class Partial(Field[Mapping[str, Any], SchemaT]):
    """Field that allows nesting of partial schemas.

    Partial schemas are schemas with a subset of fields of the
    original schema.

    Parameters
    ----------
    schema_tp: Type[:class:`Schema`]
        The schema to represent in this field.
    include: Sequence[:class:`str`]
        The list of fields to include in partial schema.
    exclude: Sequence[:class:`str`]
        The list of fields to exclude from partial schema.
    """
    __slots__ = (
        '_schema_tp',
        'include',
        'exclude',
    )

    def __init__(
            self,
            schema_tp: Type[SchemaT],
            include: Sequence[str] = MISSING,
            exclude: Sequence[str] = MISSING,
            **kwargs: Any,
        ) -> None:

        if include is not MISSING and exclude is not MISSING:
            raise TypeError('include and exclude are mutually exclusive')
        if not include and not exclude:
            raise TypeError('one of include or exclude must be provided')

        self._schema_tp = schema_tp
        self.include = set() if include is MISSING else set(include)
        self.exclude = set() if exclude is MISSING else set(exclude)
        super().__init__(**kwargs)

    @property
    def fields(self) -> Set[str]:
        """The set of field names to include in partial schema.

        This attribute is resolved using :attr:`.include` or :attr:`.exclude`.
        """
        total = set(self._schema_tp.__fields__.keys())
        if self.exclude:
            return total.difference(self.exclude)
        if self.include:
            return total.intersection(self.include)

        raise RuntimeError('This should never be reached')

    def value_set(self, value: Any, init: bool) -> SchemaT:
        if isinstance(value, collections.abc.Mapping):
            return self.value_load(value)
        if isinstance(value, self._schema_tp):
            value._transform_to_partial(include=self.fields)
            return value
        else:
            raise ValidationError(f'Value for this field must be a {self._schema_tp.__qualname__} object.')

    def value_load(self, value: Mapping[str, Any]) -> SchemaT:
        try:
            return self._schema_tp._from_partial(value, include=self.fields, from_data=True)
        except SchemaValidationFailed as err:
            raise ValidationError(err.raw()) from None

    def value_dump(self, value: Schema) -> Mapping[str, Any]:
        return value.dump()

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
from oblate import errors

import collections.abc

if TYPE_CHECKING:
    from oblate.schema import Schema
    from oblate.contexts import ErrorFormatterContext

__all__ = (
    'Object',
    'Partial',
)


class Object(Field[Mapping[str, Any], SchemaT]):
    """Field that allows nesting of schemas.

    Parameters
    ----------
    schema_type: Type[:class:`Schema`]
        The schema to represent in this field.
    """
    __slots__ = (
        'schema_type',
    )

    def __init__(self, schema_type: Type[SchemaT], **kwargs: Any) -> None:
        self.schema_type = schema_type
        super().__init__(**kwargs)

    @errors.error_formatter(errors.INVALID_DATATYPE)
    def _format_validation_error_object(self, ctx: ErrorFormatterContext) -> ValidationError:
        return ValidationError(f'Value for this field must be a {self.schema_type.__qualname__} object.')

    def value_set(self, value: Any, init: bool) -> SchemaT:
        if isinstance(value, collections.abc.Mapping):
            return self.value_load(value)
        if isinstance(value, self.schema_type):
            return value
        else:
            raise self._format_validation_error(errors.INVALID_DATATYPE, value)

    def value_load(self, value: Mapping[str, Any]) -> SchemaT:
        try:
            return self.schema_type._from_nested_object(self, value)
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
    schema_type: Type[:class:`Schema`]
        The schema to represent in this field.
    include: Sequence[:class:`str`]
        The list of fields to include in partial schema.
    exclude: Sequence[:class:`str`]
        The list of fields to exclude from partial schema.
    """
    __slots__ = (
        'schema_type',
        'include',
        'exclude',
    )

    def __init__(
            self,
            schema_type: Type[SchemaT],
            include: Sequence[str] = MISSING,
            exclude: Sequence[str] = MISSING,
            **kwargs: Any,
        ) -> None:

        if include is not MISSING and exclude is not MISSING:
            raise TypeError('include and exclude are mutually exclusive')
        if not include and not exclude:
            raise TypeError('one of include or exclude must be provided')

        self.schema_type = schema_type
        self.include = set() if include is MISSING else set(include)
        self.exclude = set() if exclude is MISSING else set(exclude)
        super().__init__(**kwargs)

    @errors.error_formatter(errors.INVALID_DATATYPE)
    def _format_validation_error_partial(self, ctx: ErrorFormatterContext) -> ValidationError:
        return ValidationError(f'Value for this field must be a {self.schema_type.__qualname__} object.')

    @property
    def fields(self) -> Set[str]:
        """The set of field names to include in partial schema.

        This attribute is resolved using :attr:`.include` or :attr:`.exclude`.
        """
        total = set(self.schema_type.__fields__.keys())
        if self.exclude:
            return total.difference(self.exclude)
        if self.include:
            return total.intersection(self.include)

        raise RuntimeError('This should never be reached')

    def value_set(self, value: Any, init: bool) -> SchemaT:
        if isinstance(value, collections.abc.Mapping):
            return self.value_load(value)
        if isinstance(value, self.schema_type):
            value._transform_to_partial(include=self.fields)
            return value
        else:
            raise self._format_validation_error(errors.INVALID_DATATYPE, value)

    def value_load(self, value: Mapping[str, Any]) -> SchemaT:
        try:
            return self.schema_type._from_partial(self, value, include=self.fields, from_data=True)
        except SchemaValidationFailed as err:
            raise ValidationError(err.raw()) from None

    def value_dump(self, value: Schema) -> Mapping[str, Any]:
        return value.dump()

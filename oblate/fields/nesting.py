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

from typing import TYPE_CHECKING, Type, Mapping, TypeVar, Any
from oblate.fields.base import Field
from oblate.schema import Schema
from oblate.exceptions import FieldError, ValidationError

import collections.abc

if TYPE_CHECKING:
    from oblate.contexts import LoadContext, DumpContext

__all__ = (
    'Object',
)

SchemaT = TypeVar('SchemaT', bound=Schema)


class Object(Field[Mapping[str, Any], SchemaT]):
    """A field that accepts :class:`Schema` objects.

    Parameters
    ----------
    schema_cls: Type[:class:`Schema`]
        The schema class that the field accepts.
    """
    __slots__ = (
        'schema_cls',
    )

    def __init__(self, schema_cls: Type[SchemaT], **kwargs: Any) -> None:
        if not issubclass(schema_cls, Schema):
            raise TypeError('schema_cls must be a subclass of Schema')

        self.schema_cls = schema_cls
        super().__init__(**kwargs)

    def value_load(self, value: Mapping[str, Any], context: LoadContext) -> SchemaT:
        if not isinstance(value, collections.abc.Mapping):
            raise FieldError(f'Value for this field must be a {self.schema_cls.__name__} object')

        try:
            return self.schema_cls(context.value)  # type: ignore
        except ValidationError as err:
            raise FieldError(err.raw()) from None

    def value_dump(self, value: SchemaT, context: DumpContext) -> Mapping[str, Any]:
        return value.dump()

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

from typing import TYPE_CHECKING, Type, Mapping, TypeVar, Any, Union
from oblate.fields.base import Field
from oblate.schema import Schema
from oblate.exceptions import FieldError, ValidationError
from oblate.utils import MISSING

import collections.abc

if TYPE_CHECKING:
    from oblate.contexts import LoadContext, DumpContext, ErrorContext

__all__ = (
    'Object',
)

SchemaT = TypeVar('SchemaT', bound=Schema)


class Object(Field[Union[Mapping[str, Any], SchemaT], SchemaT]):
    """Field that deserializes to a :class:`Schema` instance.

    This field is used for nested schemas in raw data. The first argument
    when initializing this field is the schema class that is accepted by the
    field. For example::

        class Author(oblate.Schema):
            name = fields.String()
            rating = fields.Integer()

        class Book(oblate.Schema):
            title = fields.String()
            author = fields.Object(Author)

        data = {
            'title': 'A book title',
            'author': {
                'name': 'John',
                'rating': 10,
            }
        }
        book = Book(data)
        print(book.author.name, 'has rating of', book.author.rating)  # John has rating of 10

    .. versionchanged:: 1.1

        Passing :class:`Schema` instances directly is now supported other than raw data.        

    Parameters
    ----------
    schema_cls: Type[:class:`Schema`]
        The schema class that the field accepts.
    init_kwargs: Mapping[:class:`str`, Any]
        The mapping of keyword arguments that should be passed to ``schema_cls`` while
        initializing it.

        This parameter is only taken into account when raw data is being deserialized to
        ``schema_cls``. If a ``schema_cls`` instance is passed, this parameter is ignored.

        .. versionadded:: 1.1

    Attributes
    ----------
    ERR_INVALID_DATATYPE:
        Error code raised when invalid data type is given in raw data.
    """
    ERR_INVALID_DATATYPE = 'object.invalid_datatype'

    def __init__(self, schema_cls: Type[SchemaT], *, init_kwargs: Mapping[str, Any] = MISSING, **kwargs: Any):
        if not issubclass(schema_cls, Schema):
            raise TypeError('schema_cls must be a subclass of Schema')  # pragma: no cover

        self.schema_cls = schema_cls
        self.init_kwargs: Mapping[str, Any] = init_kwargs if init_kwargs is not MISSING else {}
        super().__init__(**kwargs)

    def _get_default_error_message(self, error_code: str, context: ErrorContext) -> Union[FieldError, str]:
        if error_code == self.ERR_INVALID_DATATYPE:
            return f'Value must be a {self.schema_cls.__name__} object'

        return super()._get_default_error_message(error_code, context)  # pragma: no cover

    def value_load(self, value: Union[Mapping[str, Any], SchemaT], context: LoadContext) -> SchemaT:
        if isinstance(value, self.schema_cls):
            return value
        if isinstance(value, collections.abc.Mapping):
            try:
                return self.schema_cls(value, **self.init_kwargs)
            except ValidationError as err:
                raise FieldError(err._raw_std(include_message=False)) from None

        raise self._call_format_error(self.ERR_INVALID_DATATYPE, context.schema, value)

    def value_dump(self, value: SchemaT, context: DumpContext) -> Mapping[str, Any]:
        return value.dump()

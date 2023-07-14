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

from typing import Any, Type, TypeVar, Generic, Optional, Union, Literal, overload, TYPE_CHECKING
from typing_extensions import Self
from oblate.utils import MISSING

if TYPE_CHECKING:
    from oblate.schema import Schema

__all__ = (
    'Field',
    'String',
    'Integer',
)

_RawT = TypeVar('_RawT')
_SerializedT = TypeVar('_SerializedT')


class Field(Generic[_RawT, _SerializedT]):
    """The base class that all fields inside a schema must inherit from.

    Parameters
    ----------
    missing: :class:`bool`
        Whether this field can be missing. Set this to True to make this field
        optional. Regardless of provided value, if a ``default`` is provided,
        the value for this will automatically be set to True.
    none: :class:`bool`
        Whether this field can have a value of None.
    default:
        The value to assign to this field when it's missing. If this is not provided
        and a field is marked as missing, accessing the field at runtime would result
        in an AttributeError. 
    """
    def __init__(
            self,
            *,
            missing: bool = False,
            none: bool = False,
            default: Any = MISSING,
        ) -> None:

        self.missing = missing or (default is not MISSING)
        self.none = none
        self.default = default

        self._schema: Type[Schema] = MISSING
        self._name: str = MISSING
        self._value = MISSING

    def value_set(self, value: Any, init: bool, /) -> _SerializedT:
        """A method called when a value is being set.

        This method is called when a :class:`Schema` is initialized
        using keyword arguments or when a value is being set on a
        Schema manually. This is **not** called when a schema is
        loaded using raw data.

        You can use this method to validate a value. The returned
        value should be the value to set on the field.

        Parameters
        ----------
        value:
            The value to set.
        init: :class:`bool`
            Whether the method is called due to initialization. This is True
            when Schema is initialized and False when value is being set.
        
        Returns
        -------
        The value to set.
        """
        ...

    @overload
    def __get__(self, instance: Literal[None], owner: Type[Schema]) -> Self:
        ...

    @overload
    def __get__(self, instance: Schema, owner: Type[Schema]) -> _SerializedT:
        ...

    def __get__(self, instance: Optional[Schema], owner: Type[Schema]) -> Union[_SerializedT, Self]:
        if instance is None:
            return self
        if self._value is MISSING:
            raise AttributeError(f'No value available for field {owner.__qualname__}.{self._name}')
        return self._value

    def __set__(self, instance: Schema, value: _SerializedT) -> None:
        self._value = self.value_set(value, False)

    @property
    def schema(self) -> Type[Schema]:
        """The :class:`Schema` class that this field belongs to."""
        # self._schema should never be MISSING as it is a late-binding
        return self._schema

    @property
    def name(self) -> str:
        """The name for this class that this field belongs to."""
        # self._name should never be MISSING as it is a late-binding
        return self._name


## -- Primitive data types -- ##

class String(Field[Any, str]):
    """Representation of a string field.

    Parameters
    ----------
    strict: :class:`bool`
        Whether to only allow string data types. If this is set to False,
        any value is type casted to string. Defaults to True.
    """
    def __init__(self, *, strict: bool = True, **kwargs: Any) -> None:
        self.strict = strict
        super().__init__(**kwargs)

    def value_set(self, value: Any, init: bool) -> str:
        if not isinstance(value, str) and self.strict:
            raise RuntimeError('Value for this field must be of string data type.')

        return str(value)


class Integer(Field[Any, int]):
    """Representation of an integer field.

    Parameters
    ----------
    strict: :class:`bool`
        Whether to only allow integer data types. If this is set to False,
        any integer-castable value is type casted to integer. Defaults to True.
    """
    def __init__(self, *, strict: bool = True, **kwargs: Any) -> None:
        self.strict = strict
        super().__init__(**kwargs)

    def value_set(self, value: Any, init: bool) -> int:
        if not isinstance(value, int) and self.strict:
            raise RuntimeError('Value for this field must be of integer data type.')

        try:
            return int(value)
        except Exception:
            raise RuntimeError('Value for this field must be an integer-convertable value.')

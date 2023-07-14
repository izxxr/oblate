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

from typing import (
    Any,
    Type,
    TypeVar,
    Generic,
    Optional,
    Union,
    Literal,
    Sequence,
    Callable,
    List,
    overload,
    TYPE_CHECKING,
)
from typing_extensions import Self
from oblate.utils import MISSING

import copy

if TYPE_CHECKING:
    from oblate.schema import Schema

    ValidatorCallbackT = Callable[['_SchemaT', Any], bool]

__all__ = (
    'Field',
    'String',
    'Integer',
    'Boolean',
    'Float',
    'Object',
)


_SchemaT = TypeVar('_SchemaT', bound='Schema')
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
    __valid_overrides__ = (
        'missing',
        'none',
        'default',
    )

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
        self._validators = []
        self._clear_state()

    def _clear_state(self, validators: bool = True) -> None:
        self._schema: Type[Schema] = MISSING
        self._name: str = MISSING
        self._value = MISSING

    def _run_validators(self, value: Any) -> None:
        schema = self._schema

        for validator in self._validators:
            validated = validator(schema, value)
            if not validated:
                raise RuntimeError(f'Validation failed for field {self._name!r}')

    def add_validator(self, callback: ValidatorCallbackT[_SchemaT]) -> None:
        """Adds a validator for this field.

        Instead of using this method, consider using the :meth:`.validate`
        method for a simpler interface.

        Parameters
        ----------
        callback:
            The validator callback function.
        """
        self._validators.append(callback)

    def validate(self) -> Callable[[ValidatorCallbackT[_SchemaT]], ValidatorCallbackT[_SchemaT]]:
        """A decorator for registering a validator for this field.

        This is a much simpler interface for the :meth:`.add_validator`
        method. The decorated function takes a single parameter apart
        from self and that is the value to validate.
        """
        def __decorator(func: ValidatorCallbackT[_SchemaT]) -> ValidatorCallbackT[_SchemaT]:
            self.add_validator(func)
            return func
        return __decorator

    def remove_validator(self, callback: ValidatorCallbackT[_SchemaT]) -> None:
        """Removes a validator.

        This method does not raise any error if the given callback
        function does not exist as a validator.

        Parameters
        ----------
        callback:
            The validator callback function.
        """
        try:
            self._validators.remove(callback)
        except ValueError:
            pass

    @property
    def validators(self) -> List[ValidatorCallbackT[_SchemaT]]:
        """The list of validators for this field."""
        return self._validators.copy()

    def copy(self: Field[_RawT, _SerializedT], *, validators: bool = True, **overrides: Any) -> Field[_RawT, _SerializedT]:
        """Copies a field.

        This method is useful when you want to reuse complex fields from
        another schema without having to redefine the fields.

        Example::

            from oblate import Schema, fields

            class User(Schema):
                id = fields.Integer(strict=False)
                username = fields.String()
            
            class Game(Schema):
                id = User.id.copy()
                rating = fields.Integer()

        Parameters
        ----------
        validators: :class:`bool`
            Whether to copy field validators. When this is True, validators
            from the target field are also copied.
        **overrides:
            The keyword arguments to overriding certain attributes of field. This
            may not support all attributes of a field. Supported overrides are
            :attr:`Field.__valid_overrides__`.

        Returns
        -------
        :class:`Field`
            The copied field.
        """
        field = copy.copy(self)
        field._clear_state()

        if not validators:
            field._validators.clear()

        for arg, val in overrides.items():
            if not arg in self.__valid_overrides__:
                raise TypeError(f'{arg!r} is not a valid override keyword argument.')

            setattr(field, arg, val)

        return field

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

    def __set__(self, instance: Schema, value: Any) -> None:
        self._run_validators(value)
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


class Boolean(Field[Any, bool]):
    """Representation of a boolean field.

    Attributes
    ----------
    TRUE_VALUES: Tuple[:class:`str`, ...]
        The true values used when strict mode is off.
    FALSE_VALUES: Tuple[:class:`str`, ...]
        The false values used when strict mode is off.

    Parameters
    ----------
    strict: :class:`bool`
        Whether to only allow boolbeanb data types. If this is set to False,
        the :attr:`.TRUE_VALUES` and :attr:`FALSE_VALUES` are used to convert
        the value to boolean. Defaults to True.
    true_values: Sequence[:class:`str`]
        The values to use for true boolean conversion. Requires ``strict`` to be
        ``False`` otherwise a TypeError is raised. Defaults to :attr:`.TRUE_VALUES`.
    false_values: Sequence[:class:`str`]
        The values to use for false boolean conversion. Requires ``strict`` to be
        ``False`` otherwise a TypeError is raised. Defaults to :attr:`.FALSE_VALUES`.
    """
    TRUE_VALUES: Sequence[str] = (
        'TRUE', 'True', 'true',
        'YES', 'Yes', 'yes', '1'
    )

    FALSE_VALUES: Sequence[str] = (
        'FALSE', 'False', 'false',
        'NO', 'No', 'no', '0'
    )

    def __init__(
            self,
            *,
            strict: bool = True,
            true_values: Optional[Sequence[str]] = None,
            false_values: Optional[Sequence[str]] = None,
            **kwargs: Any,
        ) -> None:

        self.strict = strict

        if (true_values or false_values) and not strict:
            raise TypeError('strict parameter must be passed as False to use true_values/false_values')

        if not strict:
            self._true_values = true_values if true_values else self.TRUE_VALUES
            self._false_values = false_values if false_values else self.FALSE_VALUES
        else:
            self._true_values = []
            self._false_values = []

        super().__init__(**kwargs)

    def value_set(self, value: Any, init: bool) -> bool:
        if not isinstance(value, bool) and self.strict:
            raise RuntimeError('Value for this field must be of boolean type.')

        value = str(value)
        if value in self._true_values:
            return True
        if value in self._false_values:
            return False
        else:
            raise RuntimeError('Value for this field must be a boolean-convertable value.')


class Float(Field[Any, float]):
    """Representation of a float field.

    Parameters
    ----------
    strict: :class:`bool`
        Whether to only allow float data types. If this is set to False,
        any float-castable value is type casted to float. Defaults to True.
    """
    def __init__(self, *, strict: bool = True, **kwargs: Any) -> None:
        self.strict = strict
        super().__init__(**kwargs)

    def value_set(self, value: Any, init: bool) -> float:
        if not isinstance(value, float) and self.strict:
            raise RuntimeError('Value for this field must be a floating point number.')

        try:
            return float(value)
        except Exception:
            raise RuntimeError('Value for this field must be an float-convertable value.')


class Object(Field[Any, 'Schema']):
    """Field that allows nesting of schemas.

    Parameters
    ----------
    schema_tp: Type[:class:`Schema`]
        The schema to represent in this field.
    """
    def __init__(self, schema_tp: Type[Schema], **kwargs: Any) -> None:
        self._schema_tp = schema_tp
        super().__init__(**kwargs)

    def value_set(self, value: Any, init: bool) -> Schema:
        if not isinstance(value, self._schema_tp):
            raise RuntimeError(f'Value for this field must be a {self._schema_tp.__qualname__} object.')

        return value

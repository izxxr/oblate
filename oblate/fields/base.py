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
    TYPE_CHECKING,
    TypeVar,
    Generic,
    Optional,
    Any,
    Union,
    Callable,
    Type,
    List,
    Literal,
    overload,
)
from typing_extensions import Self
from oblate.utils import MISSING, bound_validation_error
from oblate.exceptions import ValidationError
from oblate import config

import copy

if TYPE_CHECKING:
    from oblate.schema import Schema

    SerializedValidatorCallbackT = Callable[['SchemaT', 'SerializedT'], bool]
    RawValidatorCallbackT = Callable[['SchemaT', 'RawT'], bool]
    ValidatorCallbackT = Union[SerializedValidatorCallbackT, RawValidatorCallbackT]

__all__ = (
    'Field',
)

RawT = TypeVar('RawT')
SerializedT = TypeVar('SerializedT')
SchemaT = TypeVar('SchemaT', bound='Schema')


class Field(Generic[RawT, SerializedT]):
    """The base class that all fields inside a schema must inherit from.

    When subclassing this class, you must implement the following abstract
    methods:

    - :meth:`.value_set`
    - :meth:`.value_load`
    - :meth:`.value_dump`

    This class is a typing generic and takes two type arguments, the first
    one being the type of raw (unserialized) value and second one being the
    type of (serialized) value to which the raw value is finally converted in.

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
    load_key: Optional[:class:`str`]
        The key that refers to this field in the data when loading this field
        using raw data.

        .. note::

            This parameter is only applicable when loading data with raw data
            i.e using the ``data`` parameter in the :class:`Schema` object and
            does not relate to argument name while initializing schema with keyword
            arguments.

    dump_key: Optional[:class:`str`]
        The key to which the deserialized value of this field should be set in the
        data returned by :meth:`Schema.dump`.
    """
    __valid_overrides__ = (
        'missing',
        'none',
        'default',
        'load_key',
        'dump_key',
    )

    __slots__ = (
        'missing',
        'none',
        'default',
        'load_key',
        'dump_key',
        '_validators',
        '_raw_validators',
        '_schema',
        '_name',
    )

    def __init__(
            self,
            *,
            missing: bool = False,
            none: bool = False,
            default: Any = MISSING,
            load_key: Optional[str] = None,
            dump_key: Optional[str] = None,
        ) -> None:

        self.missing = missing or (default is not MISSING)
        self.none = none
        self.default = default
        self.load_key = load_key
        self.dump_key = dump_key
        self._validators: List[SerializedValidatorCallbackT[Any, SerializedT]] = []
        self._raw_validators: List[RawValidatorCallbackT[Any, RawT]] = []
        self._clear_state()

    @overload
    def __get__(self, instance: Literal[None], owner: Type[Schema]) -> Self:
        ...

    @overload
    def __get__(self, instance: Schema, owner: Type[Schema]) -> SerializedT:
        ...

    def __get__(self, instance: Optional[Schema], owner: Type[Schema]) -> Union[SerializedT, Self]:
        if instance is None:
            return self
        try:
            return instance._field_values[self._name]
        except KeyError:
            raise AttributeError(f'No value available for field {owner.__qualname__}.{self._name}') from None

    def __set__(self, instance: Schema, value: Any) -> None:
        errors = []
        name = self._name
        run_validators = True
        if instance._partial and name not in instance._partial_included_fields:
            errors.append(bound_validation_error('This field cannot be set on this partial object.', self))
        else:
            if value is None:
                if self.none:
                    instance._field_values[name] = None
                else:
                    run_validators = False
                    errors.append(bound_validation_error('Value for this field cannot be None.', self))
        if not errors:
            values = instance._field_values
            old_value = values.get(name, MISSING)
            try:
                values[name] = assigned_value = self.value_set(value, False)
            except ValidationError as err:
                error = config.get_validation_fail_exception()([err], instance)
                errors.append(bound_validation_error(error.raw(), self))
            else:
                if run_validators:
                    errors.extend(self._run_validators(instance, value, raw=True))
                    errors.extend(self._run_validators(instance, assigned_value, raw=False))
                if name in instance._default_fields and not errors:
                    instance._default_fields.remove(name)
                if errors and old_value is not MISSING:
                    # Reset to old value if errors have occured
                    values[name] = old_value

        if errors:
            cls = config.get_validation_fail_exception()
            raise cls(errors, instance)

    def _clear_state(self) -> None:
        self._schema: Type[Schema] = MISSING
        self._name: str = MISSING

    def _run_validators(self, schema: Schema, value: Any, raw: bool = False) -> List[ValidationError]:
        errors = []
        validators = self._raw_validators if raw else self._validators

        for validator in validators:
            try:
                validated = validator(schema, value)
                if not validated:
                    raise ValidationError(f'Validation failed for field {self._name!r}')
            except ValidationError as err:
                err._bind(self)
                errors.append(err)

        return errors

    def _proper_name(self) -> str:
        return f'{self._schema.__qualname__}.{self._name}'

    @property
    def raw_validators(self) -> List[RawValidatorCallbackT]:
        """The list of raw validators for this field."""
        return self._raw_validators.copy()

    @property
    def validators(self) -> List[SerializedValidatorCallbackT]:
        """The list of validators for this field."""
        return self._validators.copy()

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

    def value_set(self, value: Any, init: bool, /) -> SerializedT:
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

    def value_load(self, value: RawT) -> SerializedT:
        """A method called when a value is being serialized.

        This method is called when a :class:`Schema` is initialized
        using raw data.

        You can use this method to validate or serialize a value. The
        returned value should be the value to set on the field.

        Parameters
        ----------
        value:
            The value to serialize.

        Returns
        -------
        The serialized value.
        """
        ...

    def value_dump(self, value: SerializedT) -> RawT:
        """A method called when a value is being deserialized.

        This method is called when a :class:`Schema` is being
        deserialized using :meth:`Schema.dump` method.

        You can use this method to validate or deserialize a value. The
        returned value should be the value to include in the deserialized
        data.

        Parameters
        ----------
        value:
            The value to deserialize.

        Returns
        -------
        The deserialized value.
        """
        ...

    def add_validator(self, callback: ValidatorCallbackT, *, raw: bool = False) -> None:
        """Adds a validator for this field.

        Instead of using this method, consider using the :meth:`.validate`
        method for a simpler interface.

        Parameters
        ----------
        callback:
            The validator callback function.
        raw: :class:`bool`
            Whether this is a raw validator that takes raw value rather than
            serialized one.
        """
        if raw:
            self._raw_validators.append(callback)
        else:
            self._validators.append(callback)

    def validate(self, *, raw: bool = False) -> Callable[[ValidatorCallbackT], ValidatorCallbackT]:
        """A decorator for registering a validator for this field.

        This is a much simpler interface for the :meth:`.add_validator`
        method. The decorated function takes a single parameter apart
        from self and that is the value to validate.

        This decorator takes same keyword arguments as :meth:`.add_validator`.
        """
        def __decorator(func: ValidatorCallbackT) -> ValidatorCallbackT:
            self.add_validator(func, raw=raw)
            return func
        return __decorator

    def remove_validator(self, callback: ValidatorCallbackT) -> None:
        """Removes a validator.

        This method does not raise any error if the given callback
        function does not exist as a validator.

        Parameters
        ----------
        callback:
            The validator callback function.
        """
        if callback in self._validators:
            self._validators.remove(callback)
        if callback in self._raw_validators:
            self._raw_validators.remove(callback)


    def copy(self: Field[RawT, SerializedT], *, validators: bool = True, **overrides: Any) -> Field[RawT, SerializedT]:
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
            field._raw_validators.clear()

        for arg, val in overrides.items():
            if not arg in self.__valid_overrides__:
                raise TypeError(f'{arg!r} is not a valid override keyword argument.')

            setattr(field, arg, val)

        return field

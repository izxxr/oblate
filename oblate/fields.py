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
    List,
    Set,
    Type,
    TypeVar,
    Generic,
    Optional,
    Union,
    Literal,
    Sequence,
    Callable,
    Mapping,
    overload,
    TYPE_CHECKING,
)
from typing_extensions import Self
from oblate import config
from oblate.utils import MISSING
from oblate.exceptions import ValidationError, SchemaValidationFailed

import copy
import collections.abc

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
    )

    __slots__ = (
        'missing',
        'none',
        'default',
        'load_key',
        'dump_key',
        '_validators',
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
        self._validators = []
        self._clear_state()

    @overload
    def __get__(self, instance: Literal[None], owner: Type[Schema]) -> Self:
        ...

    @overload
    def __get__(self, instance: Schema, owner: Type[Schema]) -> _SerializedT:
        ...

    def __get__(self, instance: Optional[Schema], owner: Type[Schema]) -> Union[_SerializedT, Self]:
        if instance is None:
            return self
        try:
            return instance._field_values[self._name]
        except KeyError:
            raise AttributeError(f'No value available for field {owner.__qualname__}.{self._name}') from None

    def __set__(self, instance: Schema, value: Any) -> None:
        errors = []
        if instance._partial and self._name not in instance._partial_included_fields:
            err = ValidationError('This field cannot be set on this partial object.')
            err._bind(self)
            errors.append(err)
        else:
            errors.extend(self._run_validators(instance, value))
            try:
                instance._field_values[self._name] = self.value_set(value, False)
            except ValidationError as err:
                err._bind(self)
                errors.append(err)
        if errors:
            cls = config.get_validation_fail_exception()
            raise cls(errors, instance)

    def _clear_state(self) -> None:
        self._schema: Type[Schema] = MISSING
        self._name: str = MISSING

    def _run_validators(self, schema: Schema, value: Any) -> List[ValidationError]:
        errors = []

        for validator in self._validators:
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
    def validators(self) -> List[ValidatorCallbackT[_SchemaT]]:
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

    def value_load(self, value: _RawT) -> _SerializedT:
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

    def value_dump(self, value: _SerializedT) -> _RawT:
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


## -- Primitive data types -- ##

class String(Field[Any, str]):
    """Representation of a string field.

    Parameters
    ----------
    strict: :class:`bool`
        Whether to only allow string data types. If this is set to False,
        any value is type casted to string. Defaults to True.
    """
    __slots__ = (
        'strict',
    )

    def __init__(self, *, strict: bool = True, **kwargs: Any) -> None:
        self.strict = strict
        super().__init__(**kwargs)

    def _process_value(self, value: Any) -> str:
        if not isinstance(value, str):
            if self.strict:
                raise ValidationError('Value for this field must be of string data type.')

            return str(value)
        else:
            return value

    def value_set(self, value: Any, init: bool) -> str:
        return self._process_value(value)

    def value_load(self, value: Any) -> str:
        return self._process_value(value)

    def value_dump(self, value: Any) -> str:
        return value


class Integer(Field[Any, int]):
    """Representation of an integer field.

    Parameters
    ----------
    strict: :class:`bool`
        Whether to only allow integer data types. If this is set to False,
        any integer-castable value is type casted to integer. Defaults to True.
    """
    __slots__ = (
        'strict',
    )

    def __init__(self, *, strict: bool = True, **kwargs: Any) -> None:
        self.strict = strict
        super().__init__(**kwargs)

    def _process_value(self, value: Any) -> int:
        if not isinstance(value, int):
            if self.strict:
                raise ValidationError('Value for this field must be of integer data type.')
            try:
                return int(value)
            except Exception:
                raise ValidationError('Value for this field must be an integer-convertable value.') from None
        else:
            return value 

    def value_set(self, value: Any, init: bool) -> int:
        return self._process_value(value)

    def value_load(self, value: Any) -> int:
        return self._process_value(value)

    def value_dump(self, value: Any) -> int:
        return value


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

    __slots__ = (
        'strict',
        '_true_values',
        '_false_values',
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

    def _process_value(self, value: Any) -> bool:
        if not isinstance(value, bool):
            if self.strict:
                raise ValidationError('Value for this field must be of boolean type.')
            value = str(value)
            if value in self._true_values:
                return True
            if value in self._false_values:
                return False
            else:
                raise ValidationError('Value for this field must be a boolean-convertable value.')
        else:
            return value

    def value_set(self, value: Any, init: bool) -> bool:
        return self._process_value(value)

    def value_load(self, value: Any) -> bool:
        return self._process_value(value)

    def value_dump(self, value: Any) -> bool:
        return value


class Float(Field[Any, float]):
    """Representation of a float field.

    Parameters
    ----------
    strict: :class:`bool`
        Whether to only allow float data types. If this is set to False,
        any float-castable value is type casted to float. Defaults to True.
    """
    __slots__ = (
        'strict',
    )

    def __init__(self, *, strict: bool = True, **kwargs: Any) -> None:
        self.strict = strict
        super().__init__(**kwargs)

    def _process_value(self, value: Any) -> float:
        if not isinstance(value, float):
            if self.strict:
                raise ValidationError('Value for this field must be a floating point number.')
            try:
                return float(value)
            except Exception:
                raise ValidationError('Value for this field must be an float-convertable value.') from None
        else:
            return value

    def value_set(self, value: Any, init: bool) -> float:
        return self._process_value(value)

    def value_load(self, value: Any) -> float:
        return self._process_value(value)

    def value_dump(self, value: Any) -> float:
        return value


class Object(Field[Mapping[str, Any], _SchemaT]):
    """Field that allows nesting of schemas.

    Parameters
    ----------
    schema_tp: Type[:class:`Schema`]
        The schema to represent in this field.
    """
    __slots__ = (
        '_schema_tp',
    )

    def __init__(self, schema_tp: Type[_SchemaT], **kwargs: Any) -> None:
        self._schema_tp = schema_tp
        super().__init__(**kwargs)

    def value_set(self, value: Any, init: bool) -> _SchemaT:
        if isinstance(value, collections.abc.Mapping):
            return self.value_load(value)
        if isinstance(value, self._schema_tp):
            return value
        else:
            raise ValidationError(f'Value for this field must be a {self._schema_tp.__qualname__} object.')

    def value_load(self, value: Mapping[str, Any]) -> _SchemaT:
        try:
            return self._schema_tp._from_nested_object(value)
        except SchemaValidationFailed as err:
            raise ValidationError(err.raw()) from None

    def value_dump(self, value: Schema) -> Mapping[str, Any]:
        return value.dump()


class Partial(Field[Mapping[str, Any], _SchemaT]):
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
            schema_tp: Type[_SchemaT],
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

    def value_set(self, value: Any, init: bool) -> _SchemaT:
        if isinstance(value, collections.abc.Mapping):
            return self.value_load(value)
        if isinstance(value, self._schema_tp):
            value._transform_to_partial(include=self.fields)
            return value
        else:
            raise ValidationError(f'Value for this field must be a {self._schema_tp.__qualname__} object.')

    def value_load(self, value: Mapping[str, Any]) -> _SchemaT:
        try:
            return self._schema_tp._from_partial(value, include=self.fields, from_data=True)
        except SchemaValidationFailed as err:
            raise ValidationError(err.raw()) from None

    def value_dump(self, value: Schema) -> Mapping[str, Any]:
        return value.dump()

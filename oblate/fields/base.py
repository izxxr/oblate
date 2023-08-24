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
    Any,
    Type,
    Literal,
    Optional,
    Union,
    List,
    Sequence,
    Iterator,
    overload,
)
from typing_extensions import Self
from oblate.fields.validators import Validator, ValidatorCallbackT, InputT
from oblate.utils import MISSING, current_field_name, current_schema
from oblate.exceptions import ValidationError, FieldError

import copy

if TYPE_CHECKING:
    from oblate.schema import Schema
    from oblate.contexts import LoadContext, DumpContext


__all__ = (
    'Field',
)

SchemaT = TypeVar('SchemaT', bound='Schema')
RawValueT = TypeVar('RawValueT')
SerializedValueT = TypeVar('SerializedValueT')
ValidatorT = Union[Validator[InputT], ValidatorCallbackT[SchemaT, InputT]]


class Field(Generic[RawValueT, SerializedValueT]):
    """The base class for all fields.

    All fields provided by Oblate inherit from this class. If you intend to create
    a custom field, you must use this class to inherit the field from. Subclasses
    must implement the following methods:

    - :meth:`.value_load`
    - :meth:`.value_dump`

    .. tip::

        This class is a :class:`typing.Generic` and takes two type arguments. The
        raw value type i.e the type of raw value which will be serialized to final
        value and the type of serialized value.

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
    validators: List[Union[callable, :class:`Validator`]]
        The list of validators for this field.
    """

    __slots__ = (
        'none',
        'required',
        '_default',
        '_name',
        '_schema',
        '_validators',
        '_raw_validators',
    )

    def __init__(
            self,
            *,
            none: bool = False,
            required: bool = True,
            default: Any = MISSING,
            validators: Sequence[ValidatorT[Any, Any]] = MISSING,
        ) -> None:

        self.none = none
        self.required = required and (default is MISSING)
        self._default = default
        self._validators: List[ValidatorT[SerializedValueT, Any]] = []
        self._raw_validators: List[ValidatorT[Any, Any]] = []
        self._unbind()

        if validators is not MISSING:
            for validator in validators:
                self.add_validator(validator)

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
        schema_token = current_schema.set(instance)
        field_name = current_field_name.set(self._name)
        try:
            errors = instance._process_field_value(self, value)
            if errors:
                raise ValidationError(errors)
        finally:
            current_schema.reset(schema_token)
            current_field_name.reset(field_name)

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

    def _run_validators(self, value: Any, context: LoadContext, raw: bool = False) -> List[FieldError]:
        validators = self._raw_validators if raw else self._validators
        errors: List[FieldError] = []

        for validator in validators:
            try:
                validator(context.schema, value, context)
            except (FieldError, AssertionError, ValueError) as err:
                if isinstance(err, (AssertionError, ValueError)):
                    err = FieldError._from_standard_error(err)
                errors.append(err)

        return errors

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

    def add_validator(self, validator: ValidatorT[Any, Any], *, raw: bool = False) -> None:
        """Registers a validator for this field.

        Parameters
        ----------
        validator: Union[callable, :class:`fields.Validator`]
            The validator to register. This can be a callable function or a 
            :class:`fields.Validator` instance.
        raw: :class:`bool`
            Whether a raw validator is being registered. This parameter is only
            taken into account when a callable is passed instead of a 
            :class:`fields.Validator` instance.
        """
        if not callable(validator):
            raise TypeError('validator must be a callable or Validator class instance')  # pragma: no cover

        raw = getattr(validator, '__validator_is_raw__', raw)
        self._raw_validators.append(validator) if raw else self._validators.append(validator)

    def remove_validator(self, validator: ValidatorT[Any, Any], *, raw: bool = False) -> None:
        """Removes a validator from this field.

        No error is raised if the given validator is not already registered.

        Parameters
        ----------
        validator: Union[callable, :class:`fields.Validator`]
            The validator to remove. This can be a callable function or a 
            :class:`fields.Validator` instance.
        raw: :class:`bool`
            Whether the validator being removed is raw. This parameter is only
            taken into account when a callable is passed instead of a 
            :class:`fields.Validator` instance.
        """
        if not callable(validator):
            raise TypeError('validator must be a callable or Validator class instance')  # pragma: no cover

        raw = getattr(validator, '__validator_is_raw__', raw)
        try:
            self._raw_validators.remove(validator) if raw else self._validators.remove(validator)
        except ValueError:  # pragma: no cover
            pass

    def clear_validators(self, *, raw: bool = MISSING) -> None:
        """Removes all validator from this field.

        Parameters
        ----------
        raw: :class:`bool`
            Whether to remove raw validators only. If this is not passed, all validators
            are removed. If this is True, only raw validators are removed and when False,
            only non-raw validators are removed.
        """
        if raw is MISSING:
            self._validators.clear()
            self._raw_validators.clear()
        elif raw:
            self._raw_validators.clear()
        else:
            self._validators.clear()

    def walk_validators(self, *, raw: bool = MISSING) -> Iterator[ValidatorCallbackT[Any, Any]]:
        """Iterates through the validator from this field.

        Parameters
        ----------
        raw: :class:`bool`
            Whether to iterate through raw validators only. If this is not passed,
            all validators are iterated. If this is True, only raw validators
            are iterated  and when False, only non-raw validators are iterated.
        """
        if raw is MISSING:
            validators = self._validators.copy()
            validators.extend(self._raw_validators)
        elif raw:
            validators = self._raw_validators
        else:
            validators = self._validators

        for validator in validators:
            yield validator

    def value_load(self, value: Any, context: LoadContext, /) -> SerializedValueT:
        """Serializes a raw value.

        This is an abstract method that must be implemented by subclasses. This
        method is called by the library when a field is being loaded.

        The instances when this method is called are:

        - Initializing a :class:`Schema`
        - Updating a field value on an existing :class:`Schema` instance

        The returned value is the value assigned to :class:`Schema` field
        attribute.

        Parameters
        ----------
        value:
            The value to serialize.
        context: :class:`LoadContext`
            The serialization context.

        Returns
        -------
        The serialized value.
        """
        raise NotImplementedError

    def value_dump(self, value: SerializedValueT, context: DumpContext, /) -> Any:
        """Deserializes the value to raw form.

        This is an abstract method that must be implemented by subclasses. This
        method is called by the library when a field is being dumped.

        The only time this method is called when the :meth:`Schema.dump` method
        is called. The returned value is the value included in deserialized data.

        Parameters
        ----------
        value:
            The value to deserialize.
        context: :class:`DumpContext`
            The deserialization context.

        Returns
        -------
        The deserialized value.
        """
        raise NotImplementedError

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

from typing import Optional, Mapping, Dict, Any
from typing_extensions import Self
from oblate.fields import Field
from oblate.utils import maybe_callable, MISSING
from oblate.exceptions import ValidationError, SchemaValidationFailed

import collections.abc
import inspect

__all__ = (
    'Schema',
)


class Schema:
    """The base class that all schemas must inherit from.

    Example::

        from oblate import fields
        import oblate

        class User(oblate.Schema):
            id = fields.Integer()
            name = fields.String()
            password = fields.String()
            is_employee = fields.Boolean(default=False)

            @password.validate()
            def validate_password(self, value: str) -> bool:
                if len(value) < 8:
                    raise oblate.ValidationError('Password must be greater than 8 chars')

                return True

        # Use oblate as a replacement to dataclasses
        user = User(id=1, name='John', password='123456789')
        
        # Or use it as a validation library for your REST API
        user = User({'id': 1, 'name': 'John', 'password': '1234'})

        print(user.username)
    """

    __fields__: Dict[str, Field]

    def __init__(self, data: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> None:
        self._initialized = False
        if data is not None:
            if kwargs:
                raise TypeError('Cannot mix data argument with keyword arguments')
            self._prepare(data, from_data=True)
        else:
            self._prepare(kwargs)

    def __init_subclass__(cls) -> None:
        cls.__fields__ = {}
        for name, field in inspect.getmembers(cls):
            if not isinstance(field, Field):
                continue
            
            field._schema = cls
            field._name = name
            cls.__fields__[name] = field

    @classmethod
    def _from_nested_object(cls, data: Mapping[str, Any]) -> Self:
        if not isinstance(data, collections.abc.Mapping):
            raise ValidationError(f'Value for this field must be a {cls.__qualname__} object.')
        
        return cls(data)

    def _assign_field_value(self, value: Any, field: Field[Any, Any], from_data: bool = False) -> None:
        if value is None:
            if not field.none:
                raise ValidationError('Value for this field cannot be None')
            else:
                field._value = None
            return

        if from_data:
            field._value = field.value_load(value)
        else:
            field._value = field.value_set(value, True)

    def _prepare(self, data: Mapping[str, Any], from_data: bool = False) -> None:
        fields = self.__fields__.copy()
        validators = []
        errors = []

        for arg, value in data.items():
            try:
                field = fields.pop(arg)
            except KeyError:
                if from_data:
                    errors.append(ValidationError(f'Unknown or invalid field {arg!r} provided.'))
                else:
                    raise TypeError(f'Invalid keyword argument {arg!r} passed to {self.__class__.__qualname__}()') from None
            else:
                try:
                    self._assign_field_value(value, field, from_data=True)
                except ValidationError as exc:
                    exc._bind(field)
                    errors.append(exc)

                if field.validators:
                    validators.append((field, value))

        for name, field in fields.items():
            if field.missing:
                field._value = maybe_callable(field.default)
            else:
                if from_data:
                    err = ValidationError('This field is required.')
                    err._bind(field)
                    errors.append(err)
                else:
                    raise TypeError(f'Missing value for the required field {self.__class__.__qualname__}.{name}')

        for field, value in validators:
            validator_errors = field._run_validators(self, value)
            errors.extend(validator_errors)
 
        if errors:
            raise SchemaValidationFailed(errors)

        self._initialized = True

    def is_initialized(self) -> bool:
        """Indicates whether the schema has been initialized.

        This only returns True when all fields have been set
        and validated.
        """
        return self._initialized

    def dump(self) -> Dict[str, Any]:
        """Deserializes the schema.

        The returned value is deserialized data in dictionary form.

        Returns
        -------
        Dict[:class:`str`, Any]
            The deserialized data.
        """
        out = {}
        errors = []
        for name, field in self.__fields__.items():
            if field._value is MISSING:
                if field.default is not MISSING:
                    value = maybe_callable(field.default)
                continue
            try:
                field._value = field.value_dump(field._value)
            except ValidationError as err:
                err._bind(field)
                errors.append(err)

        if errors:
            raise SchemaValidationFailed(errors)

        return out

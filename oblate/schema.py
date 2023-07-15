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

from typing import Optional, Mapping, Dict, Set, Any
from typing_extensions import Self
from oblate import config
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

    Parameters
    ----------
    data: Mapping[:class:`str`, Any]
        The data to load the schema with. Cannot be mixed with keyword
        arguments.
    **kwargs:
        The keyword arguments to initialize the schema with. Cannot be
        mixed with ``data``.
    """

    __fields__: Dict[str, Field]

    def __init__(self, data: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> None:
        if data is not None:
            if kwargs:
                raise TypeError('Cannot mix data argument with keyword arguments')
            from_data = True
        else:
            data = kwargs
            from_data= False

        self._init(data, from_data=from_data)

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
    
    @classmethod
    def _from_partial(cls, data: Mapping[str, Any], include: Set[str], from_data: bool = False) -> Self:
        if not isinstance(data, collections.abc.Mapping):
            raise ValidationError(f'Value for this field must be a partial {cls.__qualname__} object.')

        self = cls.__new__(cls)  # Bypass Schema.__init__()
        self._init(
            data,
            from_data=from_data,
            partial=True,
            partial_included_fields=include,
        )

        return self

    def _init(
            self, 
            data: Mapping[str, Any],
            from_data: bool = False,
            partial: bool = False,
            partial_included_fields: Set[str] = MISSING,
        ) -> None:

        self._partial = partial
        self._partial_included_fields = partial_included_fields
        self._initialized = False
        self._prepare(data, include=partial_included_fields, from_data=from_data)

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

    def _transform_to_partial(self, include: Set[str]) -> None:
        if self._partial:
            return

        for name, field in self.__fields__.items():
            if name not in include and field._value is not MISSING:
                raise ValidationError('This field cannot be set in this partial object.')

        self._partial = True
        self._partial_included_fields = include

    def _prepare(self, data: Mapping[str, Any], include: Set[str] = MISSING, from_data: bool = False) -> None:
        fields = self.__fields__.copy()
        validators = []
        errors = []

        for arg, value in data.items():
            try:
                field = fields.pop(arg)
            except KeyError:
                errors.append(ValidationError(f'Unknown or invalid field {arg!r} provided.'))
            else:
                if include and field._name not in include:
                    err = ValidationError(f'This field cannot be set in this partial object.')
                    err._bind(field)
                    errors.append(err)

                try:
                    self._assign_field_value(value, field, from_data=True)
                except ValidationError as exc:
                    exc._bind(field)
                    errors.append(exc)

                if field.validators:
                    validators.append((field, value))

        for name, field in fields.items():
            if include and field._name not in include:
                continue

            if field.missing:
                field._value = maybe_callable(field.default)
            else:
                err = ValidationError('This field is required.')
                err._bind(field)
                errors.append(err)

        for field, value in validators:
            validator_errors = field._run_validators(self, value)
            errors.extend(validator_errors)
 
        if errors:
            cls = config.get_validation_fail_exception()
            raise cls(errors, self)

        self._initialized = True

    def is_initialized(self) -> bool:
        """Indicates whether the schema has been initialized.

        This only returns True when all fields have been set
        and validated.
        """
        return self._initialized

    def is_partial(self) -> bool:
        """Indicates whether the schema is a partial schema (see :class:`fields.Partial` for more info)."""
        return self._partial

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
        included = self._partial_included_fields
        for name, field in self.__fields__.items():
            if included and name not in included:
                continue
            if field._value is MISSING:
                if field.default is not MISSING:
                    out[name] = maybe_callable(field.default)
                continue
            try:
                out[name] = field.value_dump(field._value)
            except ValidationError as err:
                err._bind(field)
                errors.append(err)

        if errors:
            cls = config.get_validation_fail_exception()
            raise cls(errors, self)

        return out

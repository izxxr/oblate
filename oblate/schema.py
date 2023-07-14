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

from typing import Dict, Any
from oblate.fields import Field
from oblate.utils import maybe_callable
from oblate.exceptions import ValidationError, SchemaValidationFailed

import inspect

__all__ = (
    'Schema',
)


class Schema:
    """The base class that all schemas must inherit from."""

    __fields__: Dict[str, Field]

    def __init__(self, **kwargs: Any) -> None:
        self._initialized = False
        self._init_from_kwargs(kwargs)

    def is_initialized(self) -> bool:
        """Indicates whether the schema has been initialized.

        This only returns True when all fields have been set
        and validated.
        """
        return self._initialized

    def _assign_field_value(self, value: Any, field: Field[Any, Any]) -> None:
        if value is None:
            if not field.none:
                raise ValidationError('Value for this field cannot be None')
            else:
                field._value = None
        else:
            field._value = field.value_set(value, True)

    def _init_from_kwargs(self, kwargs: Dict[str, Any]) -> None:
        fields = self.__fields__.copy()
        validators = []
        errors = []

        for arg, value in kwargs.items():
            try:
                field = fields.pop(arg)
            except KeyError:
                raise TypeError(f'Invalid keyword argument {arg!r} passed to {self.__class__.__qualname__}()') from None
            else:
                try:
                    self._assign_field_value(value, field)
                except ValidationError as exc:
                    exc._bind(field)
                    errors.append(exc)

                if field.validators:
                    validators.append((field, value))

        for name, field in fields.items():
            if field.missing:
                field._value = maybe_callable(field.default)
            else:
                raise TypeError(f'Missing value for the required field {self.__class__.__qualname__}.{name}')

        for field, value in validators:
            validator_errors = field._run_validators(value)
            errors.extend(validator_errors)
 
        if errors:
            raise SchemaValidationFailed(errors)

        self._initialized = True

    def __init_subclass__(cls) -> None:
        cls.__fields__ = {}
        for name, field in inspect.getmembers(cls):
            if not isinstance(field, Field):
                continue
            
            field._schema = cls
            field._name = name
            cls.__fields__[name] = field

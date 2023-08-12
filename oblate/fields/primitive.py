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

from typing import Any, Sequence, Optional, TYPE_CHECKING
from oblate.fields.base import Field, RawT, SerializedT
from oblate.utils import MISSING
from oblate.exceptions import ValidationError
from oblate import errors

if TYPE_CHECKING:
    from oblate.contexts import ErrorFormatterContext

__all__ = (
    'BasePrimitiveField',
    'String',
    'Integer',
    'Float',
    'Boolean',
)


class BasePrimitiveField(Field[RawT, SerializedT]):
    """Base class for fields relating to primitive data types.

    This class is a subclass of :class:`Field` and has the following
    further subclasses:

    - :class:`String`
    - :class:`Integer`
    - :class:`Float`
    - :class:`Boolean`

    Parameters
    ----------
    strict_load: :class:`bool`
        Whether to use :ref:`strict validation <tut-fields-strict-fields>` for loading fields
        using raw data.
    strict_set: :class:`bool`
        Whether to use :ref:`strict validation <tut-fields-strict-fields>` for setting fields.
    strict: :class:`bool`
        A shorthand to control the ``strict_load`` and ``strict_set`` parameters.
    """
    __slots__ = (
        'strict_set',
        'strict_load',
    )

    def __init__(
            self,
            *,
            strict_load: bool = True,
            strict_set: bool = True,
            strict: bool = MISSING,
            **kwargs: Any,
    ):
        if strict is not MISSING:
            self.strict_load = strict
            self.strict_set = strict
        else:
            self.strict_load = strict_load
            self.strict_set = strict_set
        
        super().__init__(**kwargs)

    @property
    def strict(self) -> bool:
        return self.strict_load and self.strict_set

    def _check_strict(self, load: bool, init: bool) -> bool:
        if load:
            return self.strict_load
        if init:
            return self.strict_set

        return self.strict


class String(BasePrimitiveField[Any, str]):
    """Representation of a string field.

    This class is a subclass of :class:`BasePrimitiveField` and supports
    the features documented in that class.

    Parameters
    ----------
    strict: :class:`bool`
        Whether to only allow string data types. If this is set to False,
        any value is type casted to string. Defaults to True.
    """
    _ERROR_MESSAGES = {
        errors.INVALID_DATATYPE: 'Value for this field must be of string data type.',
    }

    @errors.error_formatter(errors.INVALID_DATATYPE)
    def _format_validation_error_string(self, ctx: ErrorFormatterContext) -> ValidationError:
        return ValidationError(self._ERROR_MESSAGES[ctx.error_code])

    def _process_value(self, value: Any, load: bool, init: bool) -> str:
        if not isinstance(value, str):
            if self._check_strict(load=load, init=init):
                raise self._format_validation_error(errors.INVALID_DATATYPE, value)

            return str(value)
        else:
            return value

    def value_set(self, value: Any, init: bool) -> str:
        return self._process_value(value, load=False, init=True)

    def value_load(self, value: Any) -> str:
        return self._process_value(value, load=True, init=False)

    def value_dump(self, value: Any) -> str:
        return value


class Integer(BasePrimitiveField[Any, int]):
    """Representation of an integer field.

    This class is a subclass of :class:`BasePrimitiveField` and supports
    the features documented in that class.

    Parameters
    ----------
    strict: :class:`bool`
        Whether to only allow integer data types. If this is set to False,
        any integer-castable value is type casted to integer. Defaults to True.
    """
    _ERROR_MESSAGES = {
        errors.INVALID_DATATYPE: 'Value for this field must be of integer data type.',
        errors.NONCONVERTABLE_VALUE: 'Value for this field must be an integer-convertable value.',
    }

    @errors.error_formatter(errors.INVALID_DATATYPE, errors.NONCONVERTABLE_VALUE)
    def _format_validation_error_integer(self, ctx: ErrorFormatterContext) -> ValidationError:
        return ValidationError(self._ERROR_MESSAGES[ctx.error_code])

    def _process_value(self, value: Any, load: bool, init: bool) -> int:
        if not isinstance(value, int):
            if self._check_strict(load=load, init=init):
                raise self._format_validation_error(errors.INVALID_DATATYPE, value)
            try:
                return int(value)
            except Exception:
                raise self._format_validation_error(errors.NONCONVERTABLE_VALUE, value) from None
        else:
            return value 

    def value_set(self, value: Any, init: bool) -> int:
        return self._process_value(value, load=False, init=True)

    def value_load(self, value: Any) -> int:
        return self._process_value(value, load=True, init=False)

    def value_dump(self, value: Any) -> int:
        return value


class Boolean(BasePrimitiveField[Any, bool]):
    """Representation of a boolean field.

    This class is a subclass of :class:`BasePrimitiveField` and supports
    the features documented in that class.

    Attributes
    ----------
    TRUE_VALUES: Tuple[:class:`str`, ...]
        The true values used when strict validation is disabled.
    FALSE_VALUES: Tuple[:class:`str`, ...]
        The false values used when strict validation is disabled.

    Parameters
    ----------
    true_values: Sequence[:class:`str`]
        The values to use for true boolean conversion. These are only respected
        when :ref:`strict validation <tut-fields-strict-fields>` is disabled.

        Defaults to :attr:`.TRUE_VALUES` if not provided.
    false_values: Sequence[:class:`str`]
        The values to use for false boolean conversion. These are only respected
        when :ref:`strict validation <tut-fields-strict-fields>` is disabled.

        Defaults to :attr:`.FALSE_VALUES` if not provided.
    """
    TRUE_VALUES: Sequence[str] = (
        'TRUE', 'True', 'true',
        'YES', 'Yes', 'yes', '1'
    )

    FALSE_VALUES: Sequence[str] = (
        'FALSE', 'False', 'false',
        'NO', 'No', 'no', '0'
    )

    _ERROR_MESSAGES = {
        errors.INVALID_DATATYPE: 'Value for this field must be of boolean data type.',
        errors.NONCONVERTABLE_VALUE: 'Value for this field must be a boolean-convertable value.',
    }

    __slots__ = (
        '_true_values',
        '_false_values',
    )

    def __init__(
            self,
            *,
            true_values: Optional[Sequence[str]] = None,
            false_values: Optional[Sequence[str]] = None,
            **kwargs: Any,
        ) -> None:

        super().__init__(**kwargs)

        self._true_values = true_values if true_values is not None else self.TRUE_VALUES
        self._false_values = false_values if false_values is not None else self.FALSE_VALUES

    @errors.error_formatter(errors.INVALID_DATATYPE, errors.NONCONVERTABLE_VALUE)
    def _format_validation_error_boolean(self, ctx: ErrorFormatterContext) -> ValidationError:
        return ValidationError(self._ERROR_MESSAGES[ctx.error_code])

    def _process_value(self, value: Any, load: bool, init: bool) -> bool:
        if not isinstance(value, bool):
            if self._check_strict(load=load, init=init):
                raise self._format_validation_error(errors.INVALID_DATATYPE, value)
            value = str(value)
            if value in self._true_values:
                return True
            if value in self._false_values:
                return False
            else:
                raise self._format_validation_error(errors.NONCONVERTABLE_VALUE, value)
        else:
            return value

    def value_set(self, value: Any, init: bool) -> bool:
        return self._process_value(value, load=False, init=True)

    def value_load(self, value: Any) -> bool:
        return self._process_value(value, load=True, init=False)

    def value_dump(self, value: Any) -> bool:
        return value


class Float(BasePrimitiveField[Any, float]):
    """Representation of a float field.

    This class is a subclass of :class:`BasePrimitiveField` and supports
    the features documented in that class.

    Parameters
    ----------
    strict: :class:`bool`
        Whether to only allow float data types. If this is set to False,
        any float-castable value is type casted to float. Defaults to True.
    """
    _ERROR_MESSAGES = {
        errors.INVALID_DATATYPE: 'Value for this field must be of float data type.',
        errors.NONCONVERTABLE_VALUE: 'Value for this field must be a float-convertable value.',
    }

    @errors.error_formatter(errors.INVALID_DATATYPE, errors.NONCONVERTABLE_VALUE)
    def _format_validation_error_float(self, ctx: ErrorFormatterContext) -> ValidationError:
        return ValidationError(self._ERROR_MESSAGES[ctx.error_code])

    def _process_value(self, value: Any, load: bool, init: bool) -> float:
        if not isinstance(value, float):
            if self._check_strict(load=load, init=init):
                raise self._format_validation_error(errors.INVALID_DATATYPE, value)
            try:
                return float(value)
            except Exception:
                raise self._format_validation_error(errors.NONCONVERTABLE_VALUE, value) from None
        else:
            return value

    def value_set(self, value: Any, init: bool) -> float:
        return self._process_value(value, load=False, init=True)

    def value_load(self, value: Any) -> float:
        return self._process_value(value, load=True, init=False)

    def value_dump(self, value: Any) -> float:
        return value

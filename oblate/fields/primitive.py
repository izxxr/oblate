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

from typing import TYPE_CHECKING, Any, Optional, Sequence
from oblate.fields.base import Field
from oblate.exceptions import FieldError

if TYPE_CHECKING:
    from oblate.contexts import LoadContext, DumpContext

__all__ = (
    'String',
    'Integer',
    'Float',
    'Boolean',
)

class String(Field[str, str]):
    """Representation of a string field.

    This class is a subclass of :class:`Field` and supports
    the features documented in that class.

    Parameters
    ----------
    strict: :class:`bool`
        Whether to only allow string data types. If this is set to False,
        any value is type casted to string. Defaults to True.
    """
    __slots__ = (
        'strict',
    )

    def __init__(self, strict: bool = True, **kwargs: Any) -> None:
        self.strict = strict
        super().__init__(**kwargs)

    def _process_value(self, value: Any) -> str:
        if not isinstance(value, str):
            if self.strict:
                raise FieldError('Value of this field must be a string')

            return str(value)
        else:
            return value

    def value_load(self, context: LoadContext) -> str:
        return self._process_value(context.value)

    def value_dump(self, context: DumpContext) -> str:
        return context.value


class Integer(Field[int, int]):
    """Representation of an integer field.

    This class is a subclass of :class:`Field` and supports
    the features documented in that class.

    Parameters
    ----------
    strict: :class:`bool`
        Whether to only allow integer data types. If this is set to False,
        any integer-castable value is type casted to integer. Defaults to True.
    """
    __slots__ = (
        'strict',
    )

    def __init__(self, strict: bool = True, **kwargs: Any) -> None:
        self.strict = strict
        super().__init__(**kwargs)

    def _process_value(self, value: Any) -> int:
        if not isinstance(value, int):
            if self.strict:
                raise FieldError('Value of this field must be an integer')
            try:
                return int(value)
            except Exception:
                raise FieldError('Value of this field must be an integer-convertable value') from None
        else:
            return value

    def value_load(self, context: LoadContext) -> int:
        return self._process_value(context.value)

    def value_dump(self, context: DumpContext) -> int:
        return context.value


class Boolean(Field[bool, bool]):
    """Representation of a boolean field.

    This class is a subclass of :class:`Field` and supports
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

        super().__init__(**kwargs)

        self.strict = strict
        self._true_values = true_values if true_values is not None else self.TRUE_VALUES
        self._false_values = false_values if false_values is not None else self.FALSE_VALUES

    def _process_value(self, value: Any) -> bool:
        if not isinstance(value, bool):
            if self.strict:
                raise FieldError('Value of this field must be a boolean')
            value = str(value)
            if value in self._true_values:
                return True
            if value in self._false_values:
                return False
            else:
                raise FieldError('Value of this field must be a boolean-convertable value')
        else:
            return value

    def value_load(self, context: LoadContext) -> bool:
        return self._process_value(context.value)

    def value_dump(self, context: DumpContext) -> bool:
        return context.value


class Float(Field[float, float]):
    """Representation of a float field.

    This class is a subclass of :class:`Field` and supports
    the features documented in that class.

    Parameters
    ----------
    strict: :class:`bool`
        Whether to only allow float data types. If this is set to False,
        any float-castable value is type casted to float. Defaults to True.
    """
    __slots__ = (
        'strict',
    )

    def __init__(self, strict: bool = True, **kwargs: Any) -> None:
        self.strict = strict
        super().__init__(**kwargs)

    def _process_value(self, value: Any) -> float:
        if not isinstance(value, float):
            if self.strict:
                raise FieldError('Value of this field must be a float')
            try:
                return float(value)
            except Exception:
                raise FieldError('Value of this field must be a float-convertable value') from None
        else:
            return value

    def value_load(self, context: LoadContext) -> float:
        return self._process_value(context.value)

    def value_dump(self, context: DumpContext) -> float:
        return context.value

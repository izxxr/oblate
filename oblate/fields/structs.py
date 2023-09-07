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
    Dict as DictT,
    TypedDict as TypedDictT,
    Any,
    Union,
    TypeVar,
    Type,
)
from oblate.fields.base import Field
from oblate.exceptions import FieldError
from oblate import utils

if TYPE_CHECKING:
    from oblate.contexts import LoadContext, DumpContext, ErrorContext

__all__ = (
    'Dict',
    'TypedDict',
)

TD = TypeVar('TD', bound=TypedDictT)
KT = TypeVar('KT')
VT = TypeVar('VT')
MISSING = utils.MISSING


class Dict(Field[DictT[KT, VT], DictT[KT, VT]]):
    """A field that accepts a dictionary.

    When initialized without an argument, the field accepts any arbitrary
    dictionary. The two positional arguments correspond to the type of key
    of dictionary and type of value respectively.

    These arguments can take a type expression. For example, ``Dict(Union[str, int], bool)``
    accepts a dictionary with key of type either a string or integer and a boolean as a value.

    For more information type validation, see the :ref:`guide-type-validation` page.

    Attributes
    ----------
    ERR_INVALID_DATATYPE:
        Error raised when the given value is not a dictionary.
    ERR_TYPE_VALIDATION_FAILED:
        Error raised when the type validation fails. In this error's context,
        :attr:`ErrorContext.metadata` has a key ``type_validation_fail_errors``
        which is a list of error messages.

    Parameters
    ----------
    key_tp:
        The type of key of dictionary.
    value_tp:
        The type of value of dictionary.
    """
    __slots__ = ('_tp',)

    ERR_INVALID_DATATYPE = 'dict.invalid_datatype'
    ERR_TYPE_VALIDATION_FAILED = 'dict.type_validation_failed'

    def __init__(self, key_tp: Type[KT] = MISSING, value_tp: Type[VT] = MISSING, /, **kwargs: Any) -> None:
        if key_tp is not MISSING:
            if value_tp is MISSING:
                raise TypeError('Dict(T) is not valid, must provide a second argument for type of value')  # pragma: no cover
            self._tp = DictT[key_tp, value_tp]  # type: ignore
        else:
            self._tp = None

        super().__init__(**kwargs)

    def format_error(self, error_code: Any, context: ErrorContext) -> Union[FieldError, str]:
        if error_code == self.ERR_INVALID_DATATYPE:
            return 'Value must be a dictionary'
        if error_code == self.ERR_TYPE_VALIDATION_FAILED:
            return FieldError(context.metadata['type_validation_fail_errors'])

        return super().format_error(error_code, context)  # pragma: no cover

    def value_load(self, value: Any, context: LoadContext) -> DictT[KT, VT]:
        if not isinstance(value, dict):
            raise self._call_format_error(self.ERR_INVALID_DATATYPE, context.schema, value)
        if self._tp is not None:  # type: ignore
            validated, errors = utils.validate_struct(value, self._tp, stack_errors=True)  # type: ignore
            if not validated:
                metadata = {'type_validation_fail_errors': errors}
                raise self._call_format_error(self.ERR_TYPE_VALIDATION_FAILED, context.schema, value, metadata=metadata)
        return value  # type: ignore

    def value_dump(self, value: DictT[KT, VT], context: DumpContext) -> DictT[KT, VT]:
        return value


class TypedDict(Field[TD, TD]):
    """A field that validates from a :class:`typing.TypedDict`.

    This class provides type validation on the values of given :class:`TypedDict`,
    For more information type validation, see the :ref:`guide-type-validation` page.

    Attributes
    ----------
    ERR_INVALID_DATATYPE:
        Error raised when the given value is not a dictionary.
    ERR_TYPE_VALIDATION_FAILED:
        Error raised when the type validation fails. In this error's context,
        :attr:`ErrorContext.metadata` has a key ``type_validation_fail_errors``
        which is a list of error messages.

    Parameters
    ----------
    typed_dict: :class:`typing.TypedDict`
        The typed dictionary to validate from.
    """
    ERR_INVALID_DATATYPE = 'typed_dict.invalid_datatype'
    ERR_TYPE_VALIDATION_FAILED = 'typed_dict.type_validation_failed'

    def __init__(self, typed_dict: Type[TD], /, **kwargs: Any):
        self._typed_dict = typed_dict
        super().__init__(**kwargs)

    def format_error(self, error_code: Any, context: ErrorContext) -> Union[FieldError, str]:
        if error_code == self.ERR_INVALID_DATATYPE:
            return 'Value must be a dictionary'
        if error_code == self.ERR_TYPE_VALIDATION_FAILED:
            return FieldError(context.metadata['type_validation_fail_errors'])

        return super().format_error(error_code, context)  # pragma: no cover

    def value_load(self, value: Any, context: LoadContext) -> TD:
        if not isinstance(value, dict):
            raise self._call_format_error(self.ERR_INVALID_DATATYPE, context.schema, value)

        errors = utils.validate_typed_dict(self._typed_dict, value)  # type: ignore
        if errors:
            metadata = {'type_validation_fail_errors': errors}
            raise self._call_format_error(self.ERR_TYPE_VALIDATION_FAILED, context.schema, value, metadata=metadata)

        return value  # type: ignore

    def value_dump(self, value: TD, context: DumpContext) -> TD:
        return value
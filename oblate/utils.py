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
    Any,
    Union,
    List,
    Tuple,
    Dict,
    TypedDict,
    Literal,
    Type,
    is_typeddict,
    get_type_hints,
    get_origin,
    get_args,
    overload,
)
from typing_extensions import Required, NotRequired
from contextvars import ContextVar

import types
import collections.abc

if TYPE_CHECKING:
    from oblate.contexts import _BaseValueContext
    from oblate.schema import Schema

__all__ = (
    'MissingType',
    'MISSING',
    'current_context',
    'current_field_key',
    'validate_value',
    'validate_struct',
    'validate_typed_dict',
)

class MissingType:
    """Type for representing unaltered/default/missing values.

    Used as sentinel to differentiate between default and None values.
    utils.MISSING is a type safe instance of this class.
    """
    def __repr__(self) -> str:
        return '...'  # pragma: no cover

    def __bool__(self) -> bool:
        return False  # pragma: no cover


MISSING: Any = MissingType()


### Context variables ###

current_context: ContextVar[_BaseValueContext] = ContextVar('_current_context')
current_field_key: ContextVar[str] = ContextVar('current_field_key')
current_schema: ContextVar[Schema] = ContextVar('current_schema')


@overload
def validate_struct(value: Any, tp: Any, stack_errors: Literal[False] = False) -> Tuple[bool, str]:
    ...

@overload
def validate_struct(value: Any, tp: Any, stack_errors: Literal[True] = True) -> Tuple[bool, List[str]]:
    ...

def validate_struct(value: Any, tp: Any, stack_errors: bool = False) -> Tuple[bool, Union[List[str], str]]:
    origin = get_origin(tp)
    args = get_args(tp)
    errors: List[str] = []

    if origin is dict:
        if not isinstance(value, dict):
            return False, (['Must be a valid dictionary'] if stack_errors else 'Must be a valid dictionary')
        ktp = args[0]
        vtp = args[1]
        validated = True
        msg = ''
        for idx, (k, v) in enumerate(value.items()):  # type: ignore
            validated, fail_msg = validate_value(k, ktp)
            if not validated:
                msg = f'Dict key at index {idx}: {fail_msg}'
            else:
                validated, fail_msg = validate_value(v, vtp)
                if not validated:
                    msg = f'Dict value for key {k!r}: {fail_msg}'
            if not validated and stack_errors:
                errors.append(msg)
            if not validated and not stack_errors:
                break
        return validated, (errors if stack_errors else msg)

    if origin in (list, set, collections.abc.Sequence):
        vtp = args[0]
        if not isinstance(value, origin):
            return False, ([f'Must be a valid {origin.__name__.lower()}'] if stack_errors else f'Must be a valid {origin.__name__.lower()}')
        validated = True
        msg = ''
        for idx, v in enumerate(value):  # type: ignore
            validated, fail_msg = validate_value(v, vtp)
            if not validated:
                msg = f'Sequence item at index {idx}: {fail_msg}'
                if stack_errors:
                    errors.append(msg)  # pragma: no cover
                else:
                    break
        return validated, (errors if stack_errors else msg)

    if origin is tuple:
        if not isinstance(value, tuple):
            return False, ([f'Must be a {len(args)}-tuple'] if stack_errors else f'Must be a {len(args)}-tuple')
        validated = False
        msg = ''
        for idx, tp in enumerate(args):
            try:
                v = value[idx]  # type: ignore
            except IndexError:
                validated = False
                msg = f'Tuple length must be {len(args)} (current length: {len(value)})'  # type: ignore
                break
            else:
                validated, fail_msg = validate_value(v, tp)
                if not validated:
                    msg = f'Tuple item at index {idx}: {fail_msg}'
                    if stack_errors:
                        errors.append(msg)  # pragma: no cover
                    else:
                        break
        return validated, (errors if stack_errors else msg)

    return True, ([] if stack_errors else '')  # pragma: no cover

def validate_value(value: Any, tp: Any) -> Tuple[bool, Union[str, List[str]]]:
    origin = get_origin(tp)
    args = get_args(tp)

    if tp is Any:
        return True, ''

    if origin is None:
        if is_typeddict(tp):
            try:
                errors = validate_typed_dict(tp, value)
            except ValueError as e:  # pragma: no cover
                return False, str(e)
            else:
                if errors:
                    return False, errors[0]
                return True, ''

        return isinstance(value, tp), f'Must be of type {tp.__name__}'

    if origin in (Required, NotRequired):
        origin = get_origin(args[0])

    if origin in (list, set, dict, tuple, collections.abc.Sequence):
        return validate_struct(value, tp)

    if origin in (Union, types.UnionType):
        for tp in args:
            validated, _ = validate_value(value, tp)
            if validated:
                return True, ''
        return False, f'Must be one of types ({", ".join(tp.__name__ for tp in args)})'

    if origin is Literal:
        if value not in args:
           return False, f'Value must be one of: {", ".join(repr(v) for v in args)}'
        return True, ''

    return True, ''

def validate_typed_dict(cls: Type[TypedDict], data: Dict[Any, Any]) -> List[str]:
    if not is_typeddict(cls):
        raise TypeError('cls must be TypedDict')  # pragma: no cover
    if not isinstance(data, dict):
        raise ValueError(f'Must be a {cls.__name__} dictionary')  # pragma: no cover

    typehints = get_type_hints(cls, include_extras=True)
    errors: List[str] = []

    for key, value in data.items():
        try:
            tp = typehints.pop(key)
        except KeyError:
            errors.append(f'Invalid key {key!r}')
        else:
            validated, msg = validate_value(value, tp)
            if not validated:
                errors.append(f'Validation failed for {key!r}: {msg}')

    if not cls.__total__:
        return errors

    for key, value in typehints.items():
        if get_origin(value) is not NotRequired:
            errors.append(f'Key {key!r} is required')

    return errors
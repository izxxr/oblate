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
    Set,
    Tuple,
    Literal,
    Type,
    TypeVar,
    Generic,
    is_typeddict,
    get_type_hints,
    get_origin,
    get_args,
)
from typing_extensions import Required, NotRequired
from contextvars import ContextVar

import types
import warnings
import collections.abc

if TYPE_CHECKING:
    from oblate.contexts import _BaseValueContext
    from oblate.schema import Schema

__all__ = (
    'MissingType',
    'MISSING',
    'current_context',
    'current_field_key',
    'TypeValidator',
)

_T = TypeVar('_T')

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


class TypeValidator(Generic[_T]):
    """A class that provides and handles type validation."""
    _warning_unsupported_type = "Validation of {type} type is not supported. No type validation will " \
                                "be performed for this type by Oblate."

    _warnings_issued: Set[Any] = set()

    def __init__(self, type_expr: Type[_T]) -> None:
        self._type_expr = type_expr

    @classmethod
    def _warn_unsupported(cls, tp: Any) -> None:
        from oblate.configs import config  # circular import

        if tp in cls._warnings_issued or not config.warn_unsupported_types:
            return  # pragma: no cover

        cls._warnings_issued.add(tp)
        warnings.warn(
            cls._warning_unsupported_type.format(type=getattr(tp, '__name__', tp)),
            UserWarning,
            stacklevel=2,
        )

    @classmethod
    def _handle_type_any(cls, value: Any, tp: Any) -> Tuple[bool, List[str]]:
        return True, []

    @classmethod
    def _handle_type_typed_dict(cls, value: Any, tp: Any) -> Tuple[bool, List[str]]:
        if not isinstance(value, dict):
            return False, [f'Must be a {tp.__name__} dictionary']  # pragma: no cover

        typehints = get_type_hints(tp, include_extras=True)
        errors: List[str] = []

        for key, value in value.items():  # type: ignore
            try:
                attr_tp = typehints.pop(key)  # type: ignore
            except KeyError:
                errors.append(f'Invalid key {key!r}')
            else:
                validated, msg = cls._process_value(value, attr_tp)
                if not validated:
                    errors.append(f'Validation failed for {key!r}: {msg[0]}')

        for key, value in typehints.items():
            origin = get_origin(value)
            if (origin is None and not tp.__total__) or (origin is NotRequired):
                # either no marker and total=False -> field is not required
                # or NotRequired marker and total=True/False -> field is not required
                continue

            errors.append(f'Key {key!r} is required')

        return not errors, errors

    @classmethod
    def _handle_origin_required(cls, value: Any, tp: Any) -> Tuple[bool, List[str]]:
        args = get_args(tp)
        origin = get_origin(args[0])
        return cls._handle_origin(value, tp, origin)

    _handle_origin_not_required = _handle_origin_required

    @classmethod
    def _handle_origin_literal(cls, value: Any, tp: Any) -> Tuple[bool, List[str]]:
        args = get_args(tp)
        if value not in args:
            if len(args) == 1:
                return False, [f'Value must be equal to {args[0]!r}']
            return False, [f'Value must be one of: {", ".join(repr(v) for v in args)}']
        return True, []

    @classmethod
    def _handle_origin_union(cls, value: Any, tp: Any) -> Tuple[bool, List[str]]:
        args = get_args(tp)
        for tp in args:
            validated, _ = cls._process_value(value, tp)
            if validated:
                return True, []
        return False, [f'Type of {value!r} ({type(value).__name__}) is not compatible with types ({", ".join(tp.__name__ for tp in args)})']

    @classmethod
    def __process_mapping(cls, value: Any, tp: Any, name: str, origin: Any) -> Tuple[bool, List[str]]:
        if not isinstance(value, origin):
            return False, [f'Must be a valid {name.lower()}']

        args = get_args(tp)
        errors: List[str] = []
        validated = True
        ktp = args[0]
        vtp = args[1]

        for idx, (k, v) in enumerate(value.items()):  # type: ignore
            item_validated, fail_msg = cls._process_value(k, ktp)
            if not item_validated:
                validated = False
                errors.append(f'{name} key at index {idx}: {fail_msg[0]}')
            else:
                item_validated, fail_msg = cls._process_value(v, vtp)
                if not item_validated:
                    validated = False
                    errors.append(f'{name} value for key {k!r}: {fail_msg[0]}')

        return validated, errors

    @classmethod
    def _handle_origin_dict(cls, value: Any, tp: Any) -> Tuple[bool, List[str]]:
        return cls.__process_mapping(value, tp, 'Dictionary', dict)

    @classmethod
    def _handle_origin_mapping(cls, value: Any, tp: Any) -> Tuple[bool, List[str]]:
        return cls.__process_mapping(value, tp, 'Mapping', collections.abc.Mapping)  # pragma: no cover

    @classmethod
    def _handle_origin_list(cls, value: Any, tp: Any) -> Tuple[bool, List[str]]:
        if not isinstance(value, list):
            return False, [f'Must be a valid list']

        args = get_args(tp)
        errors: List[str] = []
        validated = True
        vtp = args[0]

        for idx, v in enumerate(value):  # type: ignore
            item_validated, fail_msg = cls._process_value(v, vtp)
            if not item_validated:
                validated = False
                errors.append(f'Sequence item at index {idx}: {fail_msg[0]}')

        return validated, errors

    @classmethod
    def _handle_origin_set(cls, value: Any, tp: Any) -> Tuple[bool, List[str]]:
        if not isinstance(value, set):
            return False, [f'Must be a valid set']

        args = get_args(tp)
        errors: List[str] = []
        validated = True
        vtp = args[0]

        for v in value:  # type: ignore
            item_validated, fail_msg = cls._process_value(v, vtp)
            if not item_validated:
                validated = False
                errors.append(f'Set includes an invalid item: {fail_msg[0]}')

        return validated, errors

    @classmethod
    def _handle_origin_tuple(cls, value: Any, tp: Any) -> Tuple[bool, List[str]]:
        if not isinstance(value, tuple):
            return False, [f'Must be a valid tuple']

        args = get_args(tp)
        errors: List[str] = []
        validated = True

        if len(args) == 2 and args[1] is Ellipsis:
            # Tuple[T, ...] -> tuple of any length of type T
            vtp = args[0]
            for idx, v in enumerate(value):  # type: ignore
                item_validated, fail_msg = cls._process_value(v, vtp)
                if not item_validated:
                    validated = False
                    errors.append(f'Tuple item at index {idx}: {fail_msg[0]}')
        else:
            for idx, tp in enumerate(args):
                try:
                    v = value[idx]  # type: ignore
                except IndexError:
                    validated = False
                    errors.append(f'Tuple length must be {len(args)} (current length: {len(value)})')  # type: ignore
                    break
                else:
                    item_validated, fail_msg = cls._process_value(v, tp)
                    if not item_validated:
                        validated = False
                        errors.append(f'Tuple item at index {idx}: {fail_msg[0]}')  # pragma: no cover

        return validated, errors

    @classmethod
    def _handle_origin_sequence(cls, value: Any, tp: Any) -> Tuple[bool, List[str]]:
        value_tp = type(value)
        if value_tp is list:
            return cls._handle_origin_list(value, tp)
        if value_tp is set:
            return cls._handle_origin_set(value, tp)
        if value_tp is tuple:
            return cls._handle_origin_tuple(value, tp)

        return cls._handle_origin_list(value, tp)  # pragma: no cover

    @classmethod
    def _process_struct(cls, value: Any, tp: Any) -> Tuple[bool, List[str]]:
        origin = get_origin(tp)

        if origin is collections.abc.Sequence:
            return cls._handle_origin_sequence(value, tp)
        if origin is dict:
            return cls._handle_origin_dict(value, tp)
        if origin is list:
            return cls._handle_origin_list(value, tp)
        if origin is set:
            return cls._handle_origin_set(value, tp)
        if origin is tuple:
            return cls._handle_origin_tuple(value, tp)

        if origin is not None:  # pragma: no cover
            cls._warn_unsupported(origin)

        return True, []  # pragma: no cover

    @classmethod
    def _handle_origin(cls, value: Any, tp: Any, origin: Any) -> Tuple[bool, List[str]]:
        if origin is Required:
            return cls._handle_origin_required(value, tp)
        if origin is NotRequired:
            return cls._handle_origin_not_required(value, tp)
        if origin in (list, set, dict, tuple, collections.abc.Sequence):
            return cls._process_struct(value, tp)
        if origin in (Union, types.UnionType):
            return cls._handle_origin_union(value, tp)
        if origin is Literal:
            return cls._handle_origin_literal(value, tp)

        if origin is not None:
            cls._warn_unsupported(origin)

        return True, []

    @classmethod
    def _process_value(cls, value: Any, tp: Any) -> Tuple[bool, List[str]]:
        if tp is Any:
            return cls._handle_type_any(value, tp)

        origin = get_origin(tp)

        if origin is None:
            if is_typeddict(tp):
                return cls._handle_type_typed_dict(value, tp)
            return isinstance(value, tp), [f'Must be of type {tp.__name__}']

        return cls._handle_origin(value, tp, origin)

    def validate(self, value: Any) -> Tuple[bool, List[str]]:
        validated, errors = self._process_value(value, self._type_expr)
        return validated, errors

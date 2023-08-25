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

from typing import Callable, Any, Type, Generic, TypeVar, Dict, Optional
from oblate.exceptions import ValidationError

__all__ = (
    'GlobalConfig',
    'config',
)

_T = TypeVar('_T')


class _ConfigOption(Generic[_T]):
    __slots__ = (
        '_default',
        '_func',
        '_name',
        '_setter',
        '__doc__',
    )

    def __init__(self, func: Callable[[GlobalConfig], _T]) -> None:
        self._default = func(None)  # type: ignore
        self._func = func
        self._name = func.__name__
        self.__doc__ = func.__doc__
        self._setter = None

    def setter(self, func: Callable[[GlobalConfig, Any], _T]) -> None:
        self._setter = func

    def __get__(self, instance: Optional[GlobalConfig], owner: Type[GlobalConfig]) -> _T:
        if instance is None:
            return self._default
        try:
            return instance._values[self._name]
        except KeyError:
            return self._default

    def __set__(self, instance: GlobalConfig, value: _T) -> None:
        if self._setter:
            value = self._setter(instance, value)

        instance._values[self._name] = value

def cfg_option(func: Callable[[GlobalConfig], _T]) -> _ConfigOption[_T]:
    return _ConfigOption(func)


class GlobalConfig:
    """The global configuration of Oblate.

    Global configuration applies to globally to each defined schema instead
    of being per-schema. The instance of this class is availabe as :data:`oblate.config`.
    The attributes of this class are available config options that can be customized.

    For more information on working with configurations, see user guide :ref:`guide-config`.
    """
    __slots__ = (
        '_values',
    )

    __config_options__ = (
        'validation_error_cls',
    )

    def __init__(self, **options: Any) -> None:
        self._values: Dict[str, Any] = {}

        for name, value in options.items():
            if not name in self.__config_options__:
                raise TypeError(f'Invalid config {name!r} in GlobalConfig()')

            self._values[name] = value

    @cfg_option
    def validation_error_cls(self) -> Type[ValidationError]:
        """The :class:`ValidationError` exception class which will be raised on validation failure."""
        return ValidationError

    @validation_error_cls.setter
    def _set_validation_error_cls(self, value: Type[ValidationError]):
        if not issubclass(value, ValidationError):
            raise TypeError('validation_error_cls must be a subclass of ValidationError')
        return value


config = GlobalConfig()
"""The global configuration of Oblate."""

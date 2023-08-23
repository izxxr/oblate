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

from typing import TYPE_CHECKING, Union, TypeVar, Callable, Generic, Any, Literal, overload

if TYPE_CHECKING:
    from oblate.fields.base import Field
    from oblate.schema import Schema
    from oblate.contexts import LoadContext


__all__ = (
    'Validator',
    'validate',
)

SchemaT = TypeVar('SchemaT', bound='Schema')
InputT = TypeVar('InputT')
ValidatorCallbackT = Callable[[SchemaT, InputT, 'LoadContext'], Any]


class Validator(Generic[InputT]):
    """The base class for validators.

    This class offers an alternative interface to the more commonly used
    :func:`fields.validate` decorator. Validators provided by Oblate inherit
    from this base class.

    Subclasses are required to override the :meth:`.validate` method.
    When subclassing, ``raw`` subclass parameter can be set to True to mark the
    validator as a :ref:`raw validator <guide-validators-raw-validator>`.

    .. tip::

        This class is a :class:`typing.Generic` and takes a single type argument, the
        type of value which will be validated.
    """
    __validator_is_raw__: bool

    def __init_subclass__(cls, raw: bool = False) -> None:
        cls.__validator_is_raw__ = raw

    def validate(self, value: InputT, context: LoadContext, /) -> Any:
        """Validates a value.

        This is an abstract method that must be implemented by the
        subclasses.

        If the validation fails, either one of :exc:`AssertionError`, :exc:`ValueError`
        or :exc:`FieldError` should be raised.

        Parameters
        ----------
        value:
            The value to validate.
        context: :class:`LoadContext`
            The serialization context.
        """
        raise NotImplementedError

    def __call__(self, schema: Schema, value: InputT, context: LoadContext, /) -> bool:
        return self.validate(value, context)


@overload
def validate(
    field: Field[Any, InputT],
    *,
    raw: Literal[False] = False,
) -> Callable[[ValidatorCallbackT[SchemaT, InputT]], ValidatorCallbackT[SchemaT, InputT]]:
    ...

@overload
def validate(
    field: Field[Any, Any],
    *,
    raw: Literal[True] = True,
) -> Callable[[ValidatorCallbackT[SchemaT, Any]], ValidatorCallbackT[SchemaT, Any]]:
    ...

@overload
def validate(
    field: str,
    *,
    raw: bool = ...,
) -> Callable[[ValidatorCallbackT[SchemaT, Any]], ValidatorCallbackT[SchemaT, Any]]:
    ...


def validate(
        field: Union[Field[Any, Any], str],
        *,
        raw: bool = False
    ) -> Callable[[ValidatorCallbackT[SchemaT, InputT]], ValidatorCallbackT[SchemaT, InputT]]:
    """A decorator to register a validator for a field.

    The decorated function takes three parameters, the schema (self), the
    value being validated and the :class:`LoadContext` instance.

    Parameters
    ----------
    field: Union[:class:`Field`, :class:`str`]
        The field or name of field that the validator is for.
    raw: :class:`bool`
        Whether the validator is a :ref:`raw validator <guide-validators-raw-validators>`.
    """
    def __wrapper(func: ValidatorCallbackT[SchemaT, InputT]) -> ValidatorCallbackT[SchemaT, InputT]:
        func.__validator_field__ = field  # type: ignore
        func.__validator_is_raw__ = raw  # type: ignore
        return func

    return __wrapper

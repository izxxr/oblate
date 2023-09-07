.. currentmodule:: oblate

.. _guide-typing-validation:

Type Validation
===============

Oblate provides robust type validation of basic type expressions. This page documents the
machinery of type validation system.

Type validation example
-----------------------

Type validation is provided by various fields. The most common examples are data structure fields such as
:class:`fields.TypedDict` or :class:`fields.Dict` etc.

Lets take :class:`fields.Dict` as an example::

    from typing import Tuple, Union

    class Model(oblate.Schema):
        data = fields.Dict(int, Union[str, Tuple[int, str]])

    Model({'data': {1: 'test'}})  # OK
    Model({'data': {2: (1, 'test')}})  # OK
    Model({'data': {1: 2}})  # Validation error

Error raised in case validation fails::

    oblate.exceptions.ValidationError:
    │
    │ 1 validation error in schema 'Model'
    │
    └── In field data:
        └── Dict value for key 1: Must be one of types (str, Tuple)

The tuple is validated too::

    Model({'data': {1: ('test', 2)}})

Results in::

    oblate.exceptions.ValidationError:
    │
    │ 1 validation error in schema 'Model'
    │
    └── In field data:
        └── Dict value for key 1: Tuple item at index 0: Must be of type int

Supported types and limitations
-------------------------------

Currently, only following types are supported:

- :class:`typing.Union`
- :class:`typing.Optional`
- :class:`typing.Literal`
- :class:`typing.Any`
- :class:`typing.Sequence`
- :class:`typing.List`
- :class:`typing.Set`
- :class:`typing.Tuple`
- :class:`typing.Dict`
- :class:`typing.TypedDict`
- :class:`typing.Required` (with typed dicts only)
- :class:`typing.NotRequired` (with typed dicts only)

Type expressions involving only these types will be validated fully. If any type expression involves
an unsupported type, it would be silently ignored.

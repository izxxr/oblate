.. currentmodule:: oblate

.. _guide-type-validation:

Type Validation
===============

Oblate provides robust type validation of basic type expressions. This page documents the
machinery of type validation system.

Type validation example
-----------------------

Type validation is provided by various fields. The most common examples are data structure fields such as
:class:`fields.TypedDict` or :class:`fields.Dict` etc.

Lets take :class:`fields.TypeExpr` as an example::

    from typing import Tuple, Union

    class Model(oblate.Schema):
        data = fields.TypeExr(Tuple[Union[str, float], int])

    Model({'data': ('3', 0)})  # OK
    Model({'data': (3.14, 3)})  # OK
    Model({'data': (3.14, 3)})  # Validation error

Error raised in case validation fails::

    oblate.exceptions.ValidationError:
    │
    │ 1 validation error in schema 'Model'
    │
    └── In field data:
        └── Tuple item at index 0: Must be one of types (str, float)


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
an unsupported type, it will not be validated. A warning will be issued by the library for usage of
an unsupported type.

To suppress unsupported type warning, set :attr:`GlobalConfig.warn_unsupported_type` warning to False.

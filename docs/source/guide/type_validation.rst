.. currentmodule:: oblate

.. _guide-type-validation:

Type Validation
===============

Oblate provides robust type validation of basic type expressions. This page documents the
machinery of type validation system.

Type validation example
-----------------------

Type validation is provided by various fields. The most common examples are data structure fields
such as :class:`fields.TypedDict` or :class:`fields.Dict` etc. The :class:`fields.TypeExpr` field
is used to validate raw type expressions.

Apart from fields, the :func:`oblate.validate_types` function is used to perform type
validation on a set of given values::

    import typing
    import oblate

    types = {
        'name': str,
        'id': typing.Union[int, str],
    }

    oblate.validate_types(types, {'name': 'John', 'id': 2})  # no error

In case the validation fails, a special exception, :exc:`oblate.TypeValidationError` is
raised. The :attr:`~oblate.TypeValidationError.errors` attribute is the dictionary including
the detail of error::

    try:
        oblate.validate_types(types, {'name': 1})
    except oblate.TypeValidationError as e:
        print(e.errors)

Error::

    {
        'name': ['Must be of type str'],
        'id': ['This key is missing.']
    }

Few parameters can be passed to this function to modify its behaviour. These are:

- ``ignore_extra``: Whether to ignore any "extra" keys passed to value mapping.
- ``ignore_missing``: Whether to ignore keys that are missing (such as ``id`` in above example).

All these parameters are, by default, False.

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
- :class:`typing.Mapping`
- :class:`typing.TypedDict`
- :class:`typing.Required` (with typed dicts only)
- :class:`typing.NotRequired` (with typed dicts only)

Type expressions involving only these types will be validated fully. If any type expression involves
an unsupported type, it will not be validated. A warning will be issued by the library for usage of
an unsupported type.

To suppress unsupported type warning, set :attr:`GlobalConfig.warn_unsupported_type` warning to False.

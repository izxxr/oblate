.. currentmodule:: oblate

.. _api-error-handling:

Error Handling
==============

Oblate provides a customizable error handling system. This allows you to use custom error
messages and formats that suit the style of your project.

This section of the API reference goes through the utilities provided by ``oblate.errors``
module that aid in customizing standard errors.

.. _api-error-handling-error-formatter:

Error Formatter
---------------

Error formatter is a function that allows you to return custom error data for standard errors. It
works in combination with :ref:`error codes <api-error-handing-error-codes>`.

Error formatters are defined inside a :class:`fields.Field` using the :func:`errors.error_formatter`
decorator.

.. autofunction:: errors.error_formatter

.. autoclass:: ErrorFormatterContext
    :members:

.. _api-error-handling-error-codes:

Error Codes
-----------

Error codes are used in customizing standard errors. These are simply integers that are used
to determine the cause of validation errors. Error codes are detailed as uppercase constants
in the ``oblate.errors`` module.

.. data:: oblate.errors.FIELD_REQUIRED

    Error indicating that a field is required but was missing during initialization
    of a schema.

    This error code has no value associated to it as such the :meth:`ErrorFormatterContext.get_value`
    method will raise a :exc:`ValueError` exception.

.. data:: oblate.errors.VALIDATION_FAILED

    Error indicating that validation failed for a field. This error is raised when
    a validator returns with a false-like value.

    The :meth:`ErrorFormatterContext.get_value` method will return the value that
    was being validated.

.. data:: oblate.errors.NONE_DISALLOWED

    Error indicating that a non-nullable field was given the value of None.

    The :meth:`ErrorFormatterContext.get_value` method will always return ``None``
    when this error is raised.

.. data:: oblate.errors.INVALID_DATATYPE

    Error indicating that the given value was of improper data type.

    This is raised when:

    - A mapping or schema object not passed to :class:`fields.Object` or :class:`fields.Partial`.
    - With strict validation enabled, improper data type passed for primitive fields.

    The :meth:`ErrorFormatterContext.get_value` method will return the value
    that has the improper type.

.. data:: oblate.errors.NONCONVERTABLE_VALUE

    Error indicating that the given value cannot be converted to the proper
    data type.

    This is raised when strict validation is disabled and a value is passed for
    primitive fields that cannot be type casted to relevant data type. For example,
    passing ``"abc"`` in :class:`~fields.Integer` field with strict validation
    disabled.

    The :meth:`ErrorFormatterContext.get_value` method will return the value
    that cannot be converted to proper data type.

.. data:: oblate.errors.DISALLOWED_FIELD

    Error indicating that the field is not allowed on a partial schema/object.

    The :meth:`ErrorFormatterContext.get_value` method returns the value the
    disallowed field has.

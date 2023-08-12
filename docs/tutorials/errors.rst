.. currentmodule:: oblate

.. _tut-error-handling:

Error Handling
==============

Oblate comes with a flexible error handling system which allows you to customize every
aspect of validation errors to match the conventions of your project.

Error Formatters
----------------

Oblate allows you to customize the error messages of standard (built in) fields. This is
done using what we refer to as "Error formatters".

Error formatter is a function defined inside a field that handles and formats validation
errors related to that field. A formatter is defined using the :func:`oblate.errors.error_formatter`
decorator::

    class CustomString(fields.String):
        @oblate.errors.error_formatter(oblate.errors.INVALID_DATATYPE)
        def handle_invalid_datatype(self, ctx):
            return ValidationError(f'{ctx.get_value()!r}: invalid data type')

    class User(oblate.Schema):
        username = CustomString()
        pin = fields.Integer()

    try:
        User(username=10, pin=1234)
    except oblate.SchemaValidationFailed as exc:
        print(exc.raw())

The output is::

    {
        "errors": [],
        "field_errors": {
            "username": ["10: invalid data type"]
        }
    }

Let us now understand what exactly is happening here. The :func:`oblate.errors.error_formatter`
decorator takes positional arguments that are error codes defined under ``oblate.errors``
representing the errors that the formatter will be handling.

``ctx`` is the :class:`ErrorFormatterContext` instance which holds useful information about
the error. The formatter must return a :exc:`ValidationError` instance.

Check the :ref:`Error Handling <api-error-handling>` section in API reference for all
available error codes.

Raw Error Format
----------------

By default, Oblate has a consistent and simple raw error format (i.e the dictionary returned by
:meth:`SchemaValidationFailed.raw` method). For advanced users, this can be customized too.

Achieving this is pretty simple, just subclass the :exc:`SchemaValidationFailed` and implement
the raw method. Finally, update the global configuration so that your subclass is used instead
of :exc:`SchemaValidationFailed`::

    class CustomFailError(SchemaValidationFailed):
        def raw(self):
            # put your implementation here
            # below is a dummy implementation
            return [error.message for error in self.errors]

    oblate.config.set_validation_fail_exception(CustomFailError)

Once this is done, ``CustomFailError`` will be raised instead of :exc:`SchemaValidationFailed`.

Errors State
------------

If you want to include any extra data with validation errors, you can use the ``state`` parameter.
You can pass anything in this parameter and access it later from somewhere else. Library will not
be manipulating this attribute.

Example::
    
    # in your validator code:
    raise ValidationError('your message', state={'error_id': 1234})
    
    # when initializing schema, you can access the state when an error
    # is raised.
    try:
        user = User(username='...')
    except SchemaValidationFailed as exc:
        for error in exc.errors:
            if error.state and 'error_id' in error.state:
                print(error.state['error_id'])

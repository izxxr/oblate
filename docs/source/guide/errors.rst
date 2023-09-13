.. currentmodule:: oblate
.. _guide-errors:

Error Handling
==============

This page covers the methods of dealing with validation errors and customizing the default error
handling system.

.. _guide-errors-intro:

Introduction
------------

It is recommended that you see the :ref:`tutorial-error-handling` section in the :ref:`tutorial` section
for a basic overview of how errors work in Oblate.

.. _guide-errors-validationerror-and-fielderror:

ValidationError and FieldError
------------------------------

It is important to understand the two primary exception classes that Oblate uses for validation errors:
:class:`FieldError` and :class:`ValidationError`.

:class:`FieldError` is raised when validation fails **for a specific field**. This error can be raised
from the user side code to indicate validation failures.

:class:`ValidationError` is raised when validation fails for a schema with one or more :class:`FieldError`.
This error is not generally raised by the user but by the library. :class:`ValidationError` can be seen
as a "wrapped" form of :class:`FieldError`. It includes all the field errors that caused the validation
failure.

In more simpler terms, you should always use :class:`ValidationError` when you are initializing or
updating a :class:`Schema` and want to catch any validation errors and you should raise the
:class:`FieldError` in your validators or other user side code to indicate validation failure.

.. _guide-errors-user-side-errors:

User side errors
----------------

When you are working with :ref:`validators <guide-validators>`, you would be raising :class:`FieldError`
to indicate validation failures.

:class:`FieldError` raised in any user side code is accounted as a validation error and it is wrapped
by the subsequently raised :class:`ValidationError`. For ease and convenience, certain standard errors
are also supported to be raised in user code to indicate validation failure. These are:

- :class:`ValueError`
- :class:`AssertionError`

This means that if you raise on of the above errors in your validators, it will automatically be
converted to a :class:`FieldError`. You can also use ``assert`` statements which makes the code
more concise.

Example::

    @validate.field('id')
    def validate_id(self, value, ctx):
        if value > 100:
            raise oblate.FieldError('Invalid ID, must be less than 100')

    # is equivalent to:

    @validate.field('id')
    def validate_id(self, value, ctx):
        assert not value > 100, 'Invalid ID, must be less than 100'

.. warning::

    It is recommended to raise :exc:`ValueError` if you intend to run your script using
    the Python's ``-O`` or ``-OO`` optimization flags. These flags remove the assertion
    statements from the code causing the validators to stop working properly.

.. _guide-errors-error-formatting:

Error formatting
----------------

When an error is raised, it is presented in a specific format. When :class:`ValidationError` is raised
and printed in the console it looks somewhat like this::

    oblate.exceptions.ValidationError:
    │
    │ 2 validation errors in schema 'User'
    │
    └── In field id:
        └── Value of this field must be an integer
    │
    └── In field username:
        └── This field is required.

Indicating each field that caused the error alongside the error message. The messages are indented
to make the error more easily readable. This format also nicely adapts to :ref:`Nested fields <guide-fields-nesting>`::

    oblate.exceptions.ValidationError:
    │
    │ 2 validation errors in schema 'Film'
    │
    └── In field actor:
        │
        └── In field name:
            └── Value of this field must be a string
    │
    └── In field rating:
        └── This field is required.

In this case, ``actor`` was a nested schema which had errors so the level of indentation increases
with level of nesting for indicating errors in nested fields.

.. _guide-errors-raw-error-formatting:

Raw error formatting
--------------------

:class:`ValidationError` can also be converted to "raw" form which is essentially a dictionary
for detailing the error. This is done by the :meth:`ValidationError.raw` method.

Example::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()
        is_employee = fields.Boolean(default=False)

    try:
        User({'id': 'invalid integer'})
    except oblate.ValidationError as err:
        print(err.raw())

Output::

    {
        'id': ['Value of this field must be an integer'],
        'username': ['This field is required.']
    }

Oblate's default raw format is a dictionary in which keys are the field names and the value is
the list of errors that were raised for that field.

This raw format can also be customized to implement your own format. This is done by subclassing the
:class:`ValidationError` and overriding the :meth:`.raw` method::

    class CustomValidationError(oblate.ValidationError):
        def raw(self):
            # your implementation here
            ...

Your implementation would make use of the :attr:`ValidationError.errors` list which includes the
:class:`FieldError` which caused the validation failure.

After that, you can change the :ref:`guide-config-global-config` so that your subclass is raised
instead of default :class:`ValidationError`::

    oblate.config.validation_error_cls = CustomValidationError

.. _guide-errors-state:

Attaching arbitrary state
-------------------------

When a :class:`FieldError` is raised, you can attach any state to it. This state can be any metadata
related to error which can be accessed later.

This is done by providing the ``state`` parameter to :class:`FieldError` which can be of any type::

    raise FieldError('error message', state={'some_key': 'value'})

Then you can access the state later at another point in your code. A common use case of this is
when you are implementing your own raw format (see the heading above) and you want to include
some extra data in it such as error codes.

Example::

    ERR_CODE_USERNAME_TOO_SHORT = 1
    ERR_CODE_PASSWORD_TOO_SHORT = 2

    class User(oblate.Schema):
        username = fields.String()
        password = fields.String()

        @validate.field(username)
        def validate_username(self, value, ctx):
            if len(value) < 5:
                state = {'error_code': ERR_CODE_USERNAME_TOO_SHORT}
                raise oblate.FieldError('Username must be more than 5 chars.', state=state)

        @validate.field(password)
        def validate_password(self, value, ctx):
            if len(value) < 8:
                state = {'error_code': ERR_CODE_PASSWORD_TOO_SHORT}
                raise oblate.FieldError('Password must be more than 8 chars.', state=state)

    try:
        User({'username': 'test', 'password': 'test'})
    except ValidationError as err:
        for error in err.errors:
            print(error.state)

Output::

    {'error_code': 1}
    {'error_code': 2}

.. _guide-errors-custom-errors:

Custom error messages
---------------------

Oblate allows customizing the default error messages. This is done by overriding the
:meth:`fields.Field.format_error` method.

The first parameter to this method is an *error code*. An error code is used to indicate the type
of error raised. All fields have the following error codes:

- :attr:`fields.Field.ERR_FIELD_REQUIRED`
- :attr:`fields.Field.ERR_NONE_DISALLOWED`
- :attr:`fields.Field.ERR_VALIDATION_FAILED`

Other error codes are specific to each field and their documentation can be found in the relevant
field's documentation.  Error codes are detailed under each field. They are upper case class attributes
prefixed with ``ERR_``.

The second parameter to :meth:`~fields.Field.format_error` is the :class:`ErrorContext` instance
holding the contextual information about the error. The method should return a :class:`str` or A
:class:`FieldError` instance.

Example::

    class Integer(fields.Integer):
        def format_error(self, error_code, ctx):
            if error_code == self.ERR_INVALID_DATATYPE:
                return f'{ctx.get_value()!r} is not an integer'

    class User(oblate.Schema):
        id = Integer()

    try:
        User({'id': 'invalid'})
    except oblate.ValidationError as err:
        print(err.raw())

Output::

    {'id': ["'invalid' is not an integer"]}

:meth:`ErrorContext.get_value` returns the value that caused the error. In case of certain
error codes, the error doesn't have a causative value. In this case, a :exc:`ValueError` is
raised. Currently, the only error that doesn't have a value is :attr:`~fields.Field.ERR_FIELD_REQUIRED`.

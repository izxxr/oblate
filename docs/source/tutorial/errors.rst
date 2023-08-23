.. currentmodule:: oblate
.. _tutorial-error-handling:

Error handling
==============

Oblate features a rich and customizable errors handling system.

Take for example, the ``User`` schema we defined earlier::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()
        is_employee = fields.Boolean(default=False)

    User({'id': 'invalid integer'})

Note that we have not provided ``username`` which is a required field and ``id`` is supposed to be an
integer, not a string. In this case, we get the following error which properly indicates the causative
fields::

    oblate.exceptions.ValidationError:
    │
    │ 2 validation errors in schema 'User'
    │
    └── In field id:
        └── Value of this field must be an integer
    │
    └── In field username:
        └── This field is required.

This error can also be converted to a "raw" format which is useful for, lets say, REST APIs::

    try:
        User({'id': 'invalid integer'})
    except oblate.ValidationError as error:
        print(error.raw())

Here's the result::

    {
        'id': ['Value of this field must be an integer'],
        'username': ['This field is required.']
    }

.. TODO: Reference error customization tutorial here

This "raw format" is fully customizable to suit any use case.

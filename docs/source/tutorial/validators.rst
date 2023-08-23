.. currentmodule:: oblate
.. _tutorial-validators:

Validators
==========

Validators are a vital part of any data validation library. Oblate, apart from providing built-in
validation features, also provides the ability of writing custom validators.

This is done using the :func:`fields.validate` function::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()
        is_employee = fields.Boolean(default=False)

        @fields.validate(id)
        def validate_id_range(self, value, ctx):
            assert value >= 1000 and value <= 9999, 'Value must be in range 1000-9999 inclusive'

Initializing the schema with invalid data::

    User({'id': 340})

causes the following error::

    oblate.exceptions.ValidationError:
    │
    │ 2 validation errors in schema 'User'
    │
    └── In field id:
        └── Value must be in range 1000-9999 inclusive
    │
    └── In field username:
        └── This field is required.


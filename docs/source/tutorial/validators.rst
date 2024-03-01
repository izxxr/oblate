.. currentmodule:: oblate
.. _tutorial-validators:

Validators
==========

Validators are a vital part of any data validation library. Oblate, apart from providing built-in
validation features, also provides the ability of writing custom validators.

This is done using the :func:`validate.field` function::

    import oblate
    from oblate import validate, fields

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()
        is_employee = fields.Boolean(default=False)

        @validate.field(id)
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

Pre-built Validators
--------------------

Some validators that are commonly used in various cases are preshipped by Oblate so you
don't have to implement such validations yourself. These validators are provided by the
``oblate.validate`` module.

For example, the range validator that we implemented above can be replaced with the one
already provided by the library::

    class User(oblate.Schema):
        id = fields.Integer(validators=[validate.Range(1000, 9999)])
        username = fields.String()
        is_employee = fields.Boolean(default=False)

The ``validators`` parameter takes a sequence of :class:`validate.Validator` objects.

It is recommended to use the pre-defined validators whenever possible as they are
tailored to be robust and flexible to suit most use cases.

These validators are documented in :ref:`Validators API Reference <api-validators>`.

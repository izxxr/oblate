.. currentmodule:: oblate
.. _tutorial-quickstart:

Quickstart
==========

This page introduces to the basics of Oblate.

Oblate's main components is the :class:`oblate.Schema` class which is used to define schemas
that can be used for validating data. Start by defining your own schema::

    from oblate import fields
    import oblate

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()
        is_employee = fields.Boolean(default=False)

Each schema has fields which are essentially just the attributes of a schema. ``oblate.fields``
provides various pre-defined commonly used fields that support standard validation rules.

Now we can use raw data to initialize our schema::

    john = User({'id': 1, 'username': 'John'})
    emily = User({'id': 2, 'username': 'Emily', 'is_employee': True})

    print(john.username, "is employee?", john.is_employee)  # John is employee? False
    print(emily.username, "is employee?", emily.is_employee)  # Emily is employee? True

Each field of the schema is accessed exactly the same way as normal attributes of a class are
accessed.

Note how the ``default`` argument was used for assigning default ``is_employee`` value
in case it is not provided in the data. There are many other similar options that
allow easy customization of each field. Some of the commonly used ones are:

- :ref:`guide-fields-optional-fields-and-defaults`
- :ref:`guide-fields-noneable-nullable-fields`
- :ref:`Strict/Non-Strict Fields <guide-fields-strict-mode>`
- :ref:`guide-fields-frozen-fields`

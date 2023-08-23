.. currentmodule:: oblate
.. _tutorial-quickstart:

Quickstart
==========

This page introduces to the basics of Oblate.

Oblate's main components is the :class:`oblate.Schema` class which is used to define schemas
that can be used for validating data. A schema is essentially a data class. Start by defining
your own schema::

    from oblate import fields
    import oblate

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()
        is_employee = fields.Boolean(default=False)

Each schema has fields which are essentially just the attributes of a schema. ``oblate.fields`` provides
various pre-defined fields that support standard validation rules.

Now we can use raw data to initialize our schema::

    john = User({'id': 1, 'username': 'John'})
    emily = User({'id': 2, 'username': 'Emily', 'is_employee': True})

    print(john.username, "is employee?", john.is_employee)  # John is employee? False
    print(emily.username, "is employee?", emily.is_employee)  # Emily is employee? True

Note how the ``default`` argument was used for defaulting ``is_employee`` value. There are many other
similar options that allow easy customization of each field.
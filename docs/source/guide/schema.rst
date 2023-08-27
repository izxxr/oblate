.. currentmodule:: oblate

.. _guide-schemas:

Schemas
=======

This page covers the features of :class:`Schema` class.

Introduction
------------

It is recommended that you see the :ref:`tutorial-quickstart` section in the :ref:`tutorial` section
for a basic overview of how schemas work in Oblate.

Schema Context
--------------

:attr:`Schema.context` is an instance of :class:`SchemaContext` class which holds useful information
about the schema and its state. See :ref:`guide-contexts` for more information about contextual objects.

Inheriting Schemas
------------------

Schemas can be inherited just like normal Python classes. Inherited schema will inherit the fields
from the parent schema.

Example::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()

    class AuthorizedUser(User):
        password = fields.String()

    # Takes all fields from user too
    AuthorizedUser({'id': 1, 'username': 'John', 'password': 'test'})

If you want to register validators in the subclassed schema for a field present in the parent, you
can use the :func:`validate.field` and pass the field name as a string.

Example::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()

    class AuthorizedUser(User):
        password = fields.String()

        @validate.field('id')
        def validate_id(self, value, ctx):
            ...

Updating schema
---------------

Schema can be updated after initialization. The Pythonic way of doing this is by simply updating
individual fields::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()
        is_employee = fields.Boolean()

    user = User({'id': 1, 'username': 'John', 'is_employee': True})
    print(user.id)  # 1

    user.id = 2
    print(user.id)  # 2

The new value is also validated and similar to initialization, an error will be raised if the
validation fails.

Another way of doing this is by using the :meth:`Schema.update` method which is suitable when
updating multiple fields or with raw data::

    user.update({'id': 2, 'username': 'Emily'})
    print(user.id, user.username, user.is_employee)  # 2 Emily True

If any of the field in the data fails validation, the schema is rolled back to previous state.

Deserializing schema
--------------------

Similar to serialization, a schema can also be deserialized. This is done using the :meth:`Schema.dump`
method.

Example::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()

    user = User({'id': 1, 'username': 'John'})
    print(user.dump())  # {'id': 1, 'username': 'John'}

If you want to deserialize specific fields only, use the ``include`` or ``exclude`` parameters (mutually
exclusive, only one can be used at a time)::

    print(user.dump(include=['id']))  # or user.dump(exclude=['username'])

Output::

    {'username': 'John'}

.. note::

    The deserialized data is not always the same as the data used to initialize
    the schema.

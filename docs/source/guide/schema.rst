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

Serializing schema
------------------

Similar to deserialization, a schema can also be deserialized. This is done using the :meth:`Schema.dump`
method.

Example::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()

    user = User({'id': 1, 'username': 'John'})
    print(user.dump())  # {'id': 1, 'username': 'John'}

If you want to serialize specific fields only, use the ``include`` or ``exclude`` parameters (mutually
exclusive, only one can be used at a time)::

    print(user.dump(include=['id']))  # or user.dump(exclude=['username'])

Output::

    {'username': 'John'}

.. note::

    The serialized data is not always the same as the data used to initialize
    the schema.

Schema State
------------

``Schema.context.state`` (:attr:`SchemaContext.state`) is used to store and propagate stateful
information which could be useful in deserialization or serialization. For more information,
see :ref:`guide-contexts-context-states`.

When initializing, the initial value of state can be set using the ``state`` parameter. This
value can be accessed and manipulated by validators or user side code.::

    schema = UserSchema(data, state={'key': 'value'})
    print(schema.context.state)  # {'key': 'value'}

Slotted Schemas
---------------

By default, all schemas have defined ``__slots__`` for performance purposes. This however, prohibits
adding custom attributes to the schema::

    class User(oblate.Schema):
        id = fields.Integer()

    user = User({'id': 1})
    user.test = 'test'  # AttributeError

In order to prevent this, it is recommended that you define your own slots::

    class User(oblate.Schema):
        __slots__ = (
            'test',
        )

        id = fields.Integer()

    user = User({'id': 1})
    user.test = 'test'  # No error

Alternatively, :attr:`SchemaConfig.slotted` can be set to ``False`` which would disable automatic
``__slots__`` setting in :class:`Schema`.

See :ref:`guide-config-schema-config` for information on manipulating schema configuration.

Representation of schema
------------------------

All schemas have a ``__repr__`` defined which returns useful information when schema is printed.

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()

    user = User({'id': 1, 'username': 'John'})
    print(user)  # User(id=1, username='John')

You can also change the default ``__repr__`` by implementing your own::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()

        def __repr__(self):
            return f'User {self.id}: {self.username}'

    user = User({'id': 1, 'username': 'John'})
    print(user)  # User 1: John

If you don't want Oblate to add a ``__repr__`` to schema, set :attr:`SchemaConfig.add_repr` to
``False``. When this is done, no ``__repr__`` would be added by Oblate and Python's default ``__repr__``
would be used.

See :ref:`guide-config-schema-config` for information on manipulating schema configuration.

Passing unknown fields
----------------------

You can dictate the behaviour when passing invalid or extra fields to the schema. By default, validation
error is raised when this is done.::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()

    user = User({'id': 1, 'username': 'John', 'extra': '1'})  # Error

Error::

    oblate.exceptions.ValidationError:
    │
    │ 1 validation error in schema 'User'
    │
    └── In field extra:
        └── Invalid or unknown field.

This can be changed by setting the :attr:`SchemaConfig.ignore_extra` option to ``True``::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()

        class Config(oblate.SchemaConfig):
            ignore_extra = True

    user = User({'id': 1, 'username': 'John', 'extra': '1'})  # extra fields silently ignored

``ignore_extra`` can be passed to :class:`Schema` initialization as keyword argument too. This
argument overrides the value defined in config. Updating the schema also supports this option.::

    user = User(data, ignore_extra=True)  # User.Config.ignore_extra ignored
    user.update(new_data, ignore_extra=True)

In both of these cases, the ``ignore_extra`` parameter takes priority over the value set for this
configuration in the schema config.

See :ref:`guide-config-schema-config` for information on manipulating schema configuration.

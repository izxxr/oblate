.. currentmodule:: oblate

Fields
======

Attributes of a schema, are what we refer to as "Fields". Oblate provides a number of commonly
used fields and also provides a way of creating custom fields for users who need it.

The Basics
----------

It is recommended that you see "Basic Usage" page in tutorials section to get a brief introduction
to how fields work on a very basic level.

Library provides a number of fields, from basic primitive data types to validating other forms
of data such as email, URLs etc.

Customizing fields
------------------

There are certain parameters that you can pass to a field to modify its behaviour.

Optional fields and defaults
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, when a field is initialized, it is marked as required as such if it is not
provided during initialization of schema, an error is raised. In some cases, you might
want to make a field "optional".

In order to do so, you will set the ``missing`` parameter to ``True``::

    class User(Schema):
        username = fields.String()
        is_employee = fields.Boolean(missing=True)

    user = User({'username': 'John'})  # No errors raised here
    user.is_employee  # AttributeError: Value for field 'is_employee' not available

Though as you may notice, when we try to access ``is_employee``, an AttributeError is raised
and in most cases, you don't want that to happen. This is when ``default`` comes into play::

    class User(Schema):
        username = fields.String()
        is_employee = fields.Boolean(default=False)

    user = User({'username': 'John'})  # No errors raised here
    user.is_employee  # False

It is worth noting that when a default is provided, the field is implicitly marked as ``missing``.

Nullable fields
~~~~~~~~~~~~~~~

You can mark certain fields to accept a value of ``None``. This is achieved using the ``none``
parameter::

    class User(Schema):
        username = fields.String()
        email = fields.String(none=True)

    User({'username': 'John', 'email': None})  # email is None!

When ``none`` is False (default), an error is raised if the given value is None. This is
library's standard validation which is performed **before** user validators are ran.

Load and Dump keys
~~~~~~~~~~~~~~~~~~

Load and dump keys are specially useful when you are receiving the data from an external
source that might use a different naming convention.

The ``load_key`` parameter defines the name of key that will point to the current field
in the given data::

    class User(Schema):
        username = fields.String()
        is_employee = fields.Boolean(load_key='isEmployee')

    user = User({'username': 'John', 'isEmployee': False})
    user.is_employee  # False
    user.isEmployee  # Error!

    user = User(username='John', isEmployee=False)  # ERROR!

It is worth noting that this parameter only is applicable when the schema is initialized using
data and not applicable when initialized with keyword arguments. Similarly, accessing the field
is always done with field name rather than the ``load_key``.

``dump_key`` works in a similar fashion but with :meth:`Schema.dump`::

    class User(Schema):
        username = fields.String()
        is_employee = fields.Boolean(dump_key='isEmployee')

    user = User({'username': 'John', 'is_employee': False})
    user.dump()  # {'username': 'John', 'isEmployee': False}

Strict Fields
~~~~~~~~~~~~~

Fields for primitive data types such as :class:`fields.String`, :class:`fields.Integer` and
:class:`fields.Boolean` etc. have a ``strict`` parameter.

When ``strict`` is True (by default), the field will only accept value that is of same data
type as field e.g. :class:`fields.String` will only accept string data type.

However, when ``strict`` is False, the provided value is converted to the relevant data
type implicitly::

    class User(Schema):
        id = fields.Integer()

    user = User({'id': '1'})  # ERROR: Must be of integer data type. 

    #### --- Without strict mode --- ###

    class User(Schema):
        id = fields.Integer(strict=False)

    user = User({'id': '1'})  # No error!
    type(user.id)  # <class 'int'>

The given value however, must be convertable to the data type otherwise an error is raised.

Nesting Schemas
~~~~~~~~~~~~~~~

Oblate also allows you to have schemas inside schemas. This is done using :class:`fields.Object`
field::


    class User(Schema):
        id = fields.Integer()
        username = fields.String()

    class Event(Schema):
        id = fields.Integer()
        host = fields.Object(User)

    data = {
        'id': 1,
        'host': {
            'id': 1,
            'username': 'Emily',
        }
    }
    event = Event(data)
    event.host.username  # Emily

The nested schema is validated separately::

    class User(Schema):
        id = fields.Integer()
        username = fields.String()

    class Event(Schema):
        id = fields.Integer()
        host = fields.Object(User)

    data = {
        'id': 1,
        'host': {
            'id': None,
            'username': 'Emily',
        }
    }
    event = Event(data)

The error message would be::

    In field host:
        In field id:
            Error: This field cannot be None.

The error data::

    {
        "errors": [],
        "field_errors": {
            "host": [
                {
                    "errors": [],
                    "field_errors": {
                        "id": [
                            "This field cannot be None."
                        ]
                }
            ]
        }
    }

Partial Schemas
~~~~~~~~~~~~~~~

Sometimes, you want to have a field that supports passing a subset of fields for a schema. This
can be achieved using :class:`fields.Partial` field::

    class User(Schema):
        id = fields.Integer()
        username = fields.String()
        is_event_host = fields.Boolean(default=False)

    class Event(Schema):
        id = fields.Integer()
        host = fields.Partial(User, include=['id', 'username']) 
        # above line can also be:
        # host = fields.Partial(User, exclude=['is_event_host'])

    event = Event({
        'id': 1,
        'host': {
            'id': 1,
            'username': 'John'
        }
    )
    event.host.is_partial()  # True


In this case, the ``is_event_host`` is excluded from the partial schema. This field cannot be
set in any way::
    
    event.host.is_event_host  # AttributeError
    event.host.is_event_host = True  # ERROR: This field cannot be set on this partial schema.

Similarly, when updating the host field, the value must have exactly those attributes set only
that are allowed in partial object::

    event.host = User(id=1, username='Emily', is_event_host=True)  # ERROR: is_event_host cannot be set here.
    event.host = User(id=1, username='Emily')  # OK!

Utilities
---------

Copying/Reusing fields
~~~~~~~~~~~~~~~~~~~~~~

Sometimes you want to reuse complex fields from other models without having to redefine them.
For that, Oblate provides you with the :meth:`fields.Field.copy` method.

Example::

    class User(Schema):
        id = fields.Integer(strict=False)
        username = fields.String()

        @id.validate()
        def validate_id(self, value: int) -> bool:
            return value > 0

    class Game(Schema):
        id = User.id.copy()

The ``copy`` method copies all the characters of field including validators. If you don't want
to include validators during copy process, you can pass ``validators=False`` in this method.

If you want to override certain attributes of field, you can pass them to copy method.

Example::

    class User(Schema):
        id = fields.Integer(strict=False, load_key='user_id')
        username = fields.String()

        @id.validate()
        def validate_id(self, value: int) -> bool:
            return value > 0

    class Game(Schema):
        id = User.id.copy(load_key='game_id')  # Override load_key

The field doesn't have to be necessarily associated to a Schema::

    id_field = fields.Integer(strict=False)

    class Game(Schema):
        id = id_field.copy()

Note that, simply doing ``id = id_field`` is not enough as each field has to be bound to a
specific schema. If you don't copy the field, you'll get unexpected errors.

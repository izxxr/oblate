.. currentmodule:: oblate

.. _guide-fields:

Fields
======

Fields are used to define the attributes of a :class:`Schema`. Oblate provides some built-in fields for
standard and commonly used data types and structures. These are available under the :mod:`oblate.fields`
package.

.. _guide-fields-defining-fields:

Defining fields
---------------

Fields are typically defined inside a :class:`Schema` subclass as class attributes. Any class attribute
inside a :class:`Schema` which is a :class:`fields.Field` instance is considered a field of that schema.

Example::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()

Here, ``id`` and ``username`` are the fields of ``User`` schema. While initializing the schema, ``id``
will accept only integers (:class:`int` type) and ``username`` will take strings (:class:`str` type).

There are also other fields provided by :mod:`oblate.fields` package similar to :class:`fields.Integer`
and :class:`fields.String` for various other data types and structures. To check out those, see the
:ref:`API reference for fields <api-fields>`.

.. _guide-fields-optional-fields-and-defaults:

Optional fields and defaults
----------------------------

By default, every field is required as such when initializing a :class:`Schema`, if that field is not
present in the given data, an error will be raised.

This behaviour can be changed. Fields can be marked as optional by using the ``required`` parameter::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()
        is_employee = fields.Boolean(required=False)

Here, ``is_employee`` is marked as optional and won't be required while initializing the schema::

    user = User({'id': 1, 'username': 'John'})

No errors will be raised by the above line. However, when accessing the field, a :exc:`ValueError`
will be raised as no value is available for this field::

    print(user.is_employee)  # ValueError: No value available for this field.
    user.is_employee = True
    print(user.is_employee)  # Prints True

This behaviour is generally not ideal. Typically, one would expect a field to default to some
value instead of raising error on access. This is done using the ``default`` parameter.

Example::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()
        is_employee = fields.Boolean(default=False)

In this case, when initializing the user schema, if the ``is_employee`` field is not given, it would
automatically get the value of ``False``. Example::

    print(User({'id': 1, 'username': 'John'}).is_employee)  # prints False

The ``default`` parameter can take any value or a callable. If a callable is given, it will be called
during field processing with two parameters: the parent :class:`~fields.Field` and the :class:`SchemaContext`
instance. The callable should return the value to set as default.

If a ``default`` is provided, field is automatically marked as optional and ``required=False`` is
not needed.

.. _guide-fields-noneable-nullable-fields:

Noneable (nullable) fields
--------------------------

By default, all fields only accept the relevant data types and do not support ``None`` values however
this can be modified.

You can mark certain fields to accept a value of ``None``. This is achieved using the ``none``
parameter::

    class User(Schema):
        username = fields.String()
        email = fields.String(none=True)

In this case, the ``email`` parameter will take either a string or a ``None`` value::

    User({'username': 'John', 'email': None})  # No error!

.. _guide-fields-strict-mode:

Strict Mode
-----------

Fields for primitive data types such as :class:`fields.String`, :class:`fields.Integer` and
:class:`fields.Boolean` etc. have a ``strict`` parameter.

When ``strict`` is True (by default), the field will only accept value that is of same data type
as field e.g. :class:`fields.String`` will only accept string data type.

However, when strict is ``False``, the provided value is converted to the relevant data
type implicitly::

    class User(Schema):
        id = fields.Integer()

    user = User({'id': '1'})  # ERROR: Must be of integer data type.

    #### --- Without strict mode --- ###

    class User(Schema):
        id = fields.Integer(strict=False)

    user = User({'id': '1'})  # No error!
    print(type(user.id), user.id)  # <class 'int'> 1

The given value however, must be convertable to the data type otherwise an error is raised.

For :class:`fields.Boolean`, with strict mode disabled, The given value is first type casted to
string and then compared against a set of values that correspond to either True or False::

    class User(Schema):
        is_employee = fields.Boolean(strict=False)

    print(User({'is_employee': 'true'}).is_employee)  # True
    print(User({'is_employee': 'TRUE'}).is_employee)  # True
    print(User({'is_employee': 'yes'}).is_employee)  # True
    print(User({'is_employee': 1}).is_employee)  # True

    print(User({'is_employee': 'false'}).is_employee)  # False
    print(User({'is_employee': 'FALSE'}).is_employee)  # False
    print(User({'is_employee': 'false'}).is_employee)  # False
    print(User({'is_employee': 0}).is_employee)  # False

    print(User({'is_employee': 'not convertable value'}).is_employee)  # ValidationError raised

It is also possible to provide the set of values that correspond to True/False::

    class User(Schema):
        is_employee = fields.Boolean(strict=False, true_values=['T', 'yeah'], false_values=['F', 'nope'])

    print(User({'is_employee': 'yeah'}).is_employee)  # True
    print(User({'is_employee': 'nope'}).is_employee)  # False
    print(User({'is_employee': 'True'}).is_employee)  # ValidationError raised

By default, ``true_values`` and ``false_values`` default to :attr:`fields.Boolean.TRUE_VALUES` and
:attr:`fields.Boolean.FALSE_VALUES` respectively.

.. _guide-fields-custom-fields:

Custom Fields
-------------

Oblate provides commonly used data types support but also allows the creation of custom fields that
have its own set of validation rules.

Fields are created by inheriting from the :class:`fields.Field` class which provides an interface
for other fields. The subclasses must implement the :meth:`~fields.Field.value_load` and
:meth:`fields.Field.value_dump` methods.

Example::

    class SumValues(fields.Field[list[int], int]):
        def value_load(self, value: list[int], ctx: oblate.LoadContext) -> int:
            if not isinstance(value, list):
                raise ValueError('Value for this field must be a list of integers')

            result = 0
            for idx, num in enumerate(value):
                if not isinstance(num, int):
                    raise ValueError(f'Non-integer value at index {idx}')

                result += num

            return result

        def value_dump(self, value: int, ctx: oblate.DumpContext) -> int:
            return value

The field above accepts a list of integers and returns their sum. The ``value_load`` method takes
two parameters:

- The value given by raw data
- The :class:`LoadContext` instance.

The raw value is any value (that could possibly be invalid too) that is provided by the data and
load context holds useful information about field serialization context. The returned value by
``value_load`` method is the serialized value that is assigned to field in the :class:`Schema`.

Example::

    class Student(oblate.Schema):
        name = fields.String()
        test_score = SumValues()

    std = Student({'name': 'John', 'test_score': [10, 9, 5, 6]})
    print(std.test_score)  # 30

The ``value_dump`` method is called when a schema is being deserialized. The value returned
by this method corresponds to the value of field in raw data. The parameters taken by this
method are:

- The serialized value that will be deserialized (i.e the value returned by ``value_load``)
- The :class:`DumpContext` instance

Example::

    std = Student({'name': 'John', 'test_score': [10, 9, 5, 6]})
    print(std.dump())  {'name': 'John', 'test_score': 30}

.. tip::

    :class:`fields.Field` is a typing generic and takes two type arguments. The first one is
    the expected raw value type and the second one is the type of serialized value.

.. _guide-fields-nesting:

Nested schemas
--------------

:class:`fields.Object` field allows nesting schemas inside other schemas. This field accepts raw data for
another schema and serializes it to the :class:`Schema` object. You can nest schemas to as many levels
as you wish.

Example::

    class Actor(oblate.Schema):
        name = fields.String()
        film_count = fields.Integer(default=0)

    class Film(oblate.Schema):
        name = fields.String()
        rating = fields.Integer()
        actor = fields.Object(Actor)

    data = {
        'name': 'A nice film',
        'rating': 10,
        'actor': {
            'name': 'John',
            'film_count': 13,
        }
    }
    film = Film(data)
    print(film.actor.name)  # John

If an error occurs in a nested schema, the causative nested fields are indicated using indentation.

Example invalid data::

    data = {
        'name': 'A nice film',
        'actor': {
            'name': 0,
            'film_count': 13,
        }
    }

Raised error::

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
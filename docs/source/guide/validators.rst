.. currentmodule:: oblate

.. _guide-validators:

Validators
==========

Apart from providing standard validation features, Oblate also provides the ability to write custom
validators.

.. _guide-validators-defining-validators:

Defining validators
-------------------

The most common and concise way of adding a validator is using the :func:`fields.validate` decorator.

Example::

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()

        @fields.validate(id)
        def validate_id(self, value: int, ctx: oblate.LoadContext):
            assert value >= 1000 and value <= 9999, 'Value must be within the 1000-9999 range'

The parameter to :func:`fields.validate` can also be a string representing the name of field.
The validator function takes two parameters apart from self, the value being validated and the
:class:`LoadContext` instance. If the validation fails, the function should not raise one of
the following errors:

- :class:`ValueError`
- :class:`AssertionError`
- :class:`FieldError`

The first two errors are automatically wrapped into a :class:`FieldError`. It is important to note
that raising any other exception would not be accounted as a validation error.

The other, less concise way of adding a validator is by using the :meth:`Field.add_validator`
function. This function takes a callback having three parameters: the schema instance, the value
being valdiated and the :class:`LoadContext` instance.

Example::

    def validate_id(schema: oblate.Schema, value: int, ctx: oblate.LoadContext):
        assert value >= 1000 and value <= 9999, 'Value must be within the 1000-9999 range'

    class User(oblate.Schema):
        id = fields.Integer()
        username = fields.String()
        id.add_validator(validate_id)

The third way of registering a validator is by passing it to field using the ``validators`` parameter::

    class User(oblate.Schema):
        id = fields.Integer(validators=[validate_id])

.. _guide-validators-raw-validators:

Raw Validators
--------------

By default, validators are ran after the serialization of raw value i.e after the :meth:`Field.value_load`
method is called. If the serialization fails, validators will not be called. This essentially means that
the ``value`` parameter will always be of correct (serialized) type.

There are also "raw validators". These validators are called with the raw, unserialized value
(the one provided in the raw data).

In order to define a raw validator, simply pass ``raw=True`` in the :func:`fields.validate` decorator
or :meth:`Field.add_validator` function.

Example::

    class User(oblate.Schema):
        id = fields.Integer(strict=False)

        @fields.validate(id, raw=True)
        def validate_id_raw(self, value, ctx: oblate.LoadContext):
            print('Raw validator got value of type', type(value))

        @fields.validate(id)
        def validate_id(self, value: int, ctx: oblate.LoadContext):
            print('Default validator got value of type', type(value))

    User({'id': '32'})

The output will be::

    Raw validator got value of type <class 'str'>
    Default validator got value of type <class 'int'>

.. warning::

    Be careful when dealing with values in raw validators, values to these validators are passed
    without prior validation. This means these validators can even have values of invalid type.

.. _guide-class-based-validators:

Class-based validators
----------------------

Sometimes it is desired for validator to take into account some data for validating a value. In this
case, class based validators are a better option. These validators are created by inheriting from the
:class:`fields.Validator` class.

Example::

    class MinLengthValidator(fields.Validator[str]):
        def __init__(self, length: int) -> None:
            self.length = length

        def validate(self, value: str, ctx: LoadContext):
            assert len(value) >= self.length

The subclasses are required to implement the :meth:`~fields.Validator.validate` method which will
perform the validation.

Adding it to the field::

    class User(oblate.Schema):
        username = fields.String(validators=[MinLengthValidator(8)])

In order to turn a class-based validator into a raw validator, the ``raw`` parameter is set to
``True`` while subclassing::

    class MinLengthValidator(fields.Validator[str], raw=True):
        ...

.. tip::

    :class:`fields.Validator` is a typing generic and takes a single type argument which is
    the expected type of value that is being validated.

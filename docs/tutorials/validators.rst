.. currentmodule:: oblate

.. _tut-validators:

Validators
==========

Validators are the most important component of any data validation library as they provide the user
the ability to write their own validation rules. Oblate provides some standard built-in validators
as well as a customizable validation system.

.. _tut-validators-standard-validators:

Standard Validations
--------------------

There are some standard validation rules that are built-in to the library. One example of these
are :ref:`tut-fields-nullable-fields`. For more information, see the :ref:`tut-fields` page.

.. _tut-validators-custom-validators:

Custom Validators
-----------------

You can also write your own validators. The conventional way of doing this is by using the
:meth:`Field.validate` decorator::
    
    class User(Schema):
        id = fields.Integer()
        username = fields.String()

        @id.validate()
        def validate_id(self, value: int) -> bool:
            return value > 0

Note that the validator function must return True if the validation passes. If it returns False,
the validation is considered to be failed and a default error message is used.

You can also have custom error messages by raising the :exc:`ValidationError` error inside the
validator function::

    class User(Schema):
        id = fields.Integer()
        username = fields.String()

        @id.validate()
        def validate_id(self, value: int) -> bool:
            if value > 0:
                raise ValidationError('ID cannot be zero or negative.')

            return True

.. note::
    
    A common pitfall is to omit the return statement. You must return True or a non-falsy value
    to indicate that the validation has passed.

.. _tut-validators-raw-validators:

Raw Validators
~~~~~~~~~~~~~~

By default, the value passed to a validator is the serialized value i.e the one that has been
returned by the field's :meth:`~fields.Field.value_load` or :meth:`~fields.Field.value_set` methods.
Sometimes you want to work with the raw value passed to the field. To achieve this, you can pass
``raw`` as True in validate decorator.

Example::
    
    from typing import Any

    class User(Schema):
        id = fields.Integer(strict=False)
        username = fields.String()

        @id.validate(raw=True)
        def validate_id_raw(self, value: Any) -> bool:
            print("Validating raw value of type", type(value))
            return True

        @id.validate()
        def validate_id_raw(self, value: Any) -> bool:
            print("Validating serialized value of type", type(value))
            return True

    User(id='2', username='John')

The output is::
    
    Validating raw value of type <class 'str'>
    Validating serialized value of type <class 'int'>

Note that while the value passed to raw validators is unserialized, these validators, like the default
ones are still called after the value setter methods.

.. _tut-validators-class-based-validators:

Class based validators
~~~~~~~~~~~~~~~~~~~~~~

Class based validators are generally useful when you want to provide some extra to validator
such as the length in length validator.

All class based validators must define a ``__call__`` method that takes two parameters apart
from self, the :class:`Schema` and value to validate.

Example::

    class MinLengthValidator:
        def __init__(self, length: int) -> None:
            self.length = length
        
        def __call__(self, schema: Schema, value: str) -> bool:
            return len(value) > self.length

    
    class User(Schema):
        id = fields.Integer(strict=False)
        username = fields.String()

        username.add_validator(MinLengthValidator(8))
        # username.add_validator(LengthValidator(8), raw=True) for raw validators

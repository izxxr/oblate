.. currentmodule:: oblate

Basic Usage
===========

Here's a quick look to what Oblate has to offer. This brief tutorial will give you a quickstart
with Oblate.

Basic look
~~~~~~~~~~

The main class of Oblate is :class:`Schema` that all schemas must inherit from::

    from oblate import fields
    import oblate

    class User(oblate.Schema):
        id = fields.Integer()
        name = fields.String()
        password = fields.String()
        is_employee = fields.Boolean(default=False)

We can now easily initialize the ``User`` object. One of the important feature of Oblate is
designed to work for all use cases.

You can either use it as a basic library for your normal classes (similar to ``dataclasses``
but with validation!)::

    user = User(id=1, name='John', password='123456789')
    print(user.username)

or use it as a data/schema validation library for REST APIs or databases::

    user = User({'id': 1, 'name': 'John', 'password': '123456789'})
    print(user.username)


Handling Errors
~~~~~~~~~~~~~~~

Oblate provides a consistent and customizable errors handling system::

    data = {
        'id': True,
        'password': '123456789',
    }
    try:
        user = User(data)  # ERRORS: Missing username field and invalid data type for id
    except SchemaValidationError as err:
        print(err.raw())

The output will be::

    {
        "errors": [],
        "field_errors": {
            "id": [
                "Value for this field must be of integer data type."
            ],
            "username": [
                "This field is required."
            ]
        }
    }

The errors handling system is highly customizable and you can easily customize the above
error format to match the style or convention of your project.

Validators
~~~~~~~~~~

Validators are an important feature of any data validation library. Certain common
validations are already part of the library such as allowing/disallowing nullable
fields etc::

    class User(oblate.Schema):
        id = fields.Integer()
        name = fields.String(none=True)  # This field can be None
        password = fields.String()
        is_employee = fields.Boolean(default=False)

However, in some cases, you might want to create your own validators. Fortunately, Oblate
makes it incredibly simple for you to acheive that::

    class User(oblate.Schema):
        id = fields.Integer()
        name = fields.String()
        password = fields.String()
        is_employee = fields.Boolean(default=False)

        @password.validate()
        def validate_password(self, value: str) -> bool:
            if len(value) < 8:
                raise oblate.ValidationError('Password must be at least 8 characters long.')
            return True

    user = User(id=1, name='John', password='12345')

The error in case the validation fail will be::

    {
        "errors": [],
        "field_errors": {
            "password": [
                "Password must be at least 8 characters long."
            ]
        }
    }

.. currentmodule:: oblate

The Schema class
================

The schema class is the main component of Oblate. All schemas must inherit from this class.

Example::

    from oblate import fields
    import oblate

    class User(oblate.Schema):
        id = fields.Integer()
        name = fields.String()
        password = fields.String()
        is_employee = fields.Boolean(default=False)

        @password.validate()
        def validate_password(self, value: str) -> bool:
            if len(value) < 8:
                raise oblate.ValidationError('Password must be greater than 8 chars')

            return True

    # Use oblate as a replacement to dataclasses
    user = User(id=1, name='John', password='123456789')
    
    # Or use it as a validation library for your REST API
    user = User({'id': 1, 'name': 'John', 'password': '1234'})

    print(user.username)


.. autoclass:: Schema
    :members:

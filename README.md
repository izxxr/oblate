# Oblate — dealing with data made easy
Oblate is a Python library that provides modern and robust interface for data and schema validation.

Focused around simplicity and flexibility, Oblate has the following features:

- Intuitive and modern object oriented interface
- Built in support for commonly used data structures
- Easily extendible to suit every use case
- Robust with no compromise on performance
- Properly type hinted to maximize the developer experience

[Documentation](https://oblate.readthedocs.io) • [Source Code](https://github.com/izxxr/oblate-v1) • [Python Package Index](https://pypi.org/project/oblate)

## Installation
Oblate is available on PyPi and can be installed using pip.
```
$ pip install oblate 
```
> **ℹ️ Didn't work?** Try prefixing the above command with `python -m` if you don't have `pip` on PATH or the command doesn't work for some reason.

## Usage
Here's a quick look to what Oblate has to offer. This brief tutorial will give you a quickstart
with Oblate.

### Basic look
The main class of Oblate is `oblate.Schema` that all schemas must inherit from.
```py
from oblate import fields
import oblate

class User(oblate.Schema):
    id = fields.Integer()
    name = fields.String()
    password = fields.String()
    is_employee = fields.Boolean(default=False)
```
We can now easily initialize the `User` object.
```py
user = User({'id': 1, 'name': 'John', 'password': '123456789'})
print(user.username)  # John
```

### Handling Errors
Oblate provides a consistent and customizable errors handling system.
```py
data = {
    'id': True,
    'password': '123456789',
}
try:
    user = User(data)  # ERRORS: Missing username field and invalid data type for id
except SchemaValidationError as err:
    print(err.raw())
```
The output will be:
```py
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
```
The errors handling system is highly customizable and you can easily customize the above
error format to match the style or convention of your project.

### Validators
Validators are an important feature of any data validation library. Certain common
validations are already part of the library such as allowing/disallowing nullable
fields etc.
```py
class User(oblate.Schema):
    id = fields.Integer()
    name = fields.String(none=True)  # This field can be None
    password = fields.String()
    is_employee = fields.Boolean(default=False)
```
However, in some cases, you might want to create your own validators. Fortunately, Oblate
makes it incredibly simple for you to acheive that.
```py
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

user = User({'id': 1, 'name': 'John', 'password': '12345'})
```
The error in case the validation fail will be:
```py
{
    "errors": [],
    "field_errors": {
        "password": [
            "Password must be at least 8 characters long."
        ]
    }
}
```

## Documentation
Oblate has a lot more to feature and discussing all of that here is not possible. Check the
[Oblate's documentation](https://oblate.readthedocs.io) that includes examples and pages to get
you started with using Oblate for your project along with details on all the features Oblate has.


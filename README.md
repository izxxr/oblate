# Oblate — data, made easy
Oblate is a Python library that provides modern and robust interface for data and schema validation.

Focused around simplicity and flexibility, Oblate has the following features:

- Intuitive and modern object oriented interface
- Built in support for commonly used data structures
- Easily extendible and customizable to suit every use case
- Robust with no compromise on performance and speed
- Typed and plays well with static type checking

[Documentation](https://oblate.readthedocs.io) • [Source Code](https://github.com/izxxr/oblate) • [Python Package Index](https://pypi.org/project/oblate)

## Installation
Oblate is available on PyPi and can be installed using pip.
```
$ pip install oblate 
```
> **ℹ️ Didn't work?** Try prefixing the above command with `python -m` if you don't have `pip` on PATH or the command doesn't work for some reason.

## Usage
Oblate is focused around simplicity and ease of usage. Below snippet is an example of how data
is handled using Oblate:
```py
from oblate import validate, fields
import oblate

# A schema defines the structure of data
class Author(oblate.Schema):
    name = fields.String()  # Field must be a string
    bio = fields.String(none=True)  # Field allows None to be passed
    rating = fields.Integer(default=0)  # Optional field that defaults to 0

    # Apply custom validations to a field
    @validate.field(rating)
    def validate_rating(self, value, ctx):
        assert value >= 0 and value <= 10, 'Rating must be in range 0-10 inclusive'

class Book(oblate.Schema):
    title = fields.String()
    price = fields.Float()
    author = fields.Object(Author)

data = {
    'title': 'Art of Data Validation',
    'price': 20.30,
    'author': {
        'name': 'John',
        'bio': None,
        'rating': 4,
    }
}
book = Book(data)
print(f"{book.title} by {book.author.name}")
```
Check the [**Quickstart**](https://oblate.readthedocs.io/en/latest/tutorial/index.html) section in
documentation for an introduction to the basics of library.

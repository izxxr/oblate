# MIT License

# Copyright (c) 2023 Izhar Ahmad

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from typing import Any
from oblate import fields

import oblate
import pytest

def test_validator():
    class User(oblate.Schema):
        id = fields.Integer()

        @fields.validate(id)
        def validate_id(self, value: int, context: oblate.LoadContext):
            if not (value >= 1000 and value <= 9999):
                raise ValueError

    assert User({'id': 3210}).id == 3210

    with pytest.raises(oblate.ValidationError, match='Validation failed'):
        User({'id': 320})


class _RangeValidator(fields.Validator[int]):
    def __init__(self, lb: int, ub: int) -> None:
        self.lb = lb
        self.ub = ub

    def validate(self, value: int, context: oblate.LoadContext) -> Any:
        if not (value >= self.lb and value <= self.ub):
            raise ValueError('Value must be in range 1000-9999')

def test_class_validator():
    class User(oblate.Schema):
        id = fields.Integer(strict=False, validators=[_RangeValidator(1000, 9999)])

    assert User({'id': '3210'}).id == 3210

    with pytest.raises(oblate.ValidationError, match='in range 1000-9999'):
        User({'id': 320})

class User(oblate.Schema):
    id = fields.Integer(strict=False)

    @fields.validate('id', raw=True)
    def validate_raw_id(self, value: str, context: oblate.LoadContext):
        assert isinstance(value, str)

    @fields.validate('id', raw=False)
    def validate_id(self, value: int, context: oblate.LoadContext):
        if not (value >= 1000 and value <= 9999):
            raise ValueError('Value must be in range 1000-9999')

def test_raw_validator():
    assert User({'id': '3210'}).id == 3210

    with pytest.raises(oblate.ValidationError, match='in range 1000-9999'):
        User({'id': 320})

def test_validators_methods():
    assert list(User.id.walk_validators()) == [User.validate_id, User.validate_raw_id]
    assert list(User.id.walk_validators(raw=True)) == [User.validate_raw_id]
    assert list(User.id.walk_validators(raw=False)) == [User.validate_id]

    User.id.remove_validator(User.validate_id)

    assert list(User.id.walk_validators()) == [User.validate_raw_id]

    range_validator = _RangeValidator(1000, 9999)
    User.id.add_validator(range_validator)
    User.id.add_validator(User.validate_id)
    assert list(User.id.walk_validators()) == [range_validator,  User.validate_id, User.validate_raw_id]

    User.id.clear_validators(raw=True)
    assert list(User.id.walk_validators()) == [range_validator, User.validate_id]

    User.id.clear_validators(raw=False)
    assert list(User.id.walk_validators()) == []

    User.id.add_validator(range_validator)
    User.id.add_validator(User.validate_id)
    User.id.add_validator(User.validate_raw_id)
    User.id.clear_validators()
    assert list(User.id.walk_validators()) == []
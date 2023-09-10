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
from oblate import fields, validate

import oblate
import pytest

def test_validator():
    class User(oblate.Schema):
        id = fields.Integer()

        @validate.field(id)
        def validate_id(self, value: int, context: oblate.LoadContext):
            if not (value >= 1000 and value <= 9999):
                raise ValueError

    assert User({'id': 3210}).id == 3210

    with pytest.raises(oblate.ValidationError, match='Validation failed'):
        User({'id': 320})


class _RangeValidator(validate.Validator[int]):
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

    @validate.field('id', raw=True)
    def validate_raw_id(self, value: str, context: oblate.LoadContext):
        assert isinstance(value, str)

    @validate.field('id', raw=False)
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


def test_validators_range():
    msg = 'Value must be in range {lb} to {ub} inclusive'

    class User(oblate.Schema):
        id = fields.Integer(validators=[validate.Range(1000, 9999)])

    assert User({'id': 1020}).id == 1020
    assert User({'id': 1000}).id == 1000
    assert User({'id': 9999}).id == 9999

    with pytest.raises(oblate.ValidationError, match=msg.format(lb='1000', ub='9999')):
        User({'id': 900})
    with pytest.raises(oblate.ValidationError, match=msg.format(lb='1000', ub='9999')):
        User({'id': 10000})

    class UserNoUB(oblate.Schema):
        id = fields.Integer(validators=[validate.Range(10)])

    assert UserNoUB({'id': 10}).id == 10
    assert UserNoUB({'id': 0}).id == 0

    with pytest.raises(oblate.ValidationError, match=msg.format(lb='0', ub='10')):
        UserNoUB({'id': -2})
    with pytest.raises(oblate.ValidationError, match=msg.format(lb='0', ub='10')):
        UserNoUB({'id': 11})

    class UserStd(oblate.Schema):
        id = fields.Integer(validators=[validate.Range.from_standard(range(5))])  # 0, 1, 2, 3, 4

    assert UserStd({'id': 2}).id == 2
    assert UserStd({'id': 4}).id == 4

    with pytest.raises(oblate.ValidationError, match=msg.format(lb='0', ub='4')):
        UserStd({'id': 5})

    class UserExact(oblate.Schema):
        id = fields.Integer(validators=[validate.Range(2, 2)])

    assert UserExact({'id': 2}).id == 2

    with pytest.raises(oblate.ValidationError, match='Value must be equal to 2'):
        UserExact({'id': 5})

def test_validator_length():
    class _Schema(oblate.Schema):
        minl = fields.String(validators=[validate.Length(min=5)], default=0)
        maxl = fields.String(validators=[validate.Length(max=5)], default=0)
        rangel = fields.String(validators=[validate.Length(min=5, max=10)], default=0)
        exactl = fields.String(validators=[validate.Length(exact=5)], default=0)

    assert _Schema({'minl': '123456'})
    assert _Schema({'minl': '12345'})

    with pytest.raises(oblate.ValidationError, match='Value length must be greater than 5 characters'):
        _Schema({'minl': '1234'})

    assert _Schema({'maxl': '123'})
    assert _Schema({'maxl': '12345'})

    with pytest.raises(oblate.ValidationError, match='Value length must be less than 5 characters'):
        _Schema({'maxl': '123456'})

    assert _Schema({'rangel': '12345'})
    assert _Schema({'rangel': '1234567'})
    assert _Schema({'rangel': '1234567890'})

    with pytest.raises(oblate.ValidationError, match='Value length must be between 5 to 10 characters'):
        _Schema({'rangel': '12345678900'})

    with pytest.raises(oblate.ValidationError, match='Value length must be between 5 to 10 characters'):
        _Schema({'rangel': '1234'})

    assert _Schema({'exactl': '12345'})

    with pytest.raises(oblate.ValidationError, match='Value length must be exactly 5 characters'):
        _Schema({'exactl': '1234'})

    with pytest.raises(oblate.ValidationError, match='Value length must be exactly 5 characters'):
        _Schema({'exactl': '123456'})

def test_validator_exclude():
    class _Schema(oblate.Schema):
        single = fields.String(validators=[validate.Exclude('ex1')], default='New Folder')
        multiple = fields.String(validators=[validate.Exclude('ex1', 'ex2', 'ex3')], default=0)

    assert _Schema({'single': 'test'})
    assert _Schema({'multiple': 'test'})

    with pytest.raises(oblate.ValidationError, match="Value cannot be 'ex1'"):
        _Schema({'single': 'ex1'})

    with pytest.raises(oblate.ValidationError, match="Value cannot be one from: 'ex1', 'ex2', 'ex3'"):
        _Schema({'multiple': 'ex2'})

def test_validator_or():
    def validator_func(s: oblate.Schema, v: str, c: oblate.LoadContext):
        assert v.startswith('s_')

    validators = [
        validate.Length(min=5),
        validator_func,
    ]

    class _Schema(oblate.Schema):
        val_or = fields.String(validators=[validate.Or(*validators)])

    assert _Schema({'val_or': '123456'})
    assert _Schema({'val_or': '12345'})
    assert _Schema({'val_or': 's_1'})
    assert _Schema({'val_or': 's_2'})

    with pytest.raises(oblate.ValidationError, match="All validations failed for the given value"):
        _Schema({'val_or': 'test'})

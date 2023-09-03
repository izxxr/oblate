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

from oblate import fields
import oblate
import pytest

class _TestSchemaStrict(oblate.Schema):
    string = fields.String()
    integer = fields.Integer()
    float_ = fields.Float()
    boolean = fields.Boolean()

class _TestSchemaNoStrict(oblate.Schema):
    string = fields.String(strict=False)
    integer = fields.Integer(strict=False)
    float_ = fields.Float(strict=False)
    boolean = fields.Boolean(strict=False)

def test_nostrict_fields():
    nostrict = _TestSchemaNoStrict({
        'string': 123,
        'integer': '30',
        'float_': '3.14',
        'boolean': 'yes',
    })

    assert nostrict.string == '123'
    assert nostrict.integer == 30
    assert nostrict.float_ == 3.14
    assert nostrict.boolean == True

def test_string_strictness():
    with pytest.raises(oblate.ValidationError, match='Value must be a string'):
        _TestSchemaStrict({
            'string': 123,
            'integer': '123',
            'float_': 3.14,
            'boolean': True,
        })

def test_integer_strictness():
    with pytest.raises(oblate.ValidationError, match="Failed to coerce 'invalid int' to integer"):
        _TestSchemaNoStrict({
            'string': 123,
            'integer': 'invalid int',
            'float_': 3.14,
            'boolean': True,
        })

    with pytest.raises(oblate.ValidationError, match='Value must be an integer'):
        _TestSchemaStrict({
            'string': 123,
            'integer': '123',
            'float_': 3.14,
            'boolean': True,
        })

def test_float_strictness():
    with pytest.raises(oblate.ValidationError, match="Failed to coerce 'bad float' to float"):
        _TestSchemaNoStrict({
            'string': 123,
            'integer': 1234,
            'float_': 'bad float',
            'boolean': True,
        })

    with pytest.raises(oblate.ValidationError, match='Value must be a float'):
        _TestSchemaStrict({
            'string': 123,
            'integer': 123,
            'float_': '3.14',
            'boolean': True,
        })


def test_boolean_strictness():
    with pytest.raises(oblate.ValidationError, match="Failed to coerce 'bad boolean' to boolean"):
        _TestSchemaNoStrict({
            'string': 123,
            'integer': 123,
            'float_': 3.14,
            'boolean': 'bad boolean',
        })

    with pytest.raises(oblate.ValidationError, match='Value must be a boolean'):
        _TestSchemaStrict({
            'string': 123,
            'integer': 123,
            'float_': 3.14,
            'boolean': 'true',
        })


def test_boolean_values():
    class _TestSchema(oblate.Schema):
        boolean = fields.Boolean(true_values=['true 1'], strict=False)

    assert _TestSchema({'boolean': 'true 1'}).boolean == True
    assert _TestSchema({'boolean': '0'}).boolean == False

    with pytest.raises(oblate.ValidationError, match="Failed to coerce 'bad boolean' to boolean"):
        _TestSchema({'boolean': 'bad boolean'})

def test_dump():
    test = _TestSchemaNoStrict({
        'string': 1234,
        'integer': '60',
        'float_': '9.0',
        'boolean': 'yes',
    })
    expected_dump = {
        'string': '1234',
        'integer': 60,
        'float_': 9.0,
        'boolean': True,
    }

    assert test.dump() == expected_dump
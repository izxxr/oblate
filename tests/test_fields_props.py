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

def test_nullable_fields():
    class _TestSchema(oblate.Schema):
        field = fields.String()
        nullable_field = fields.String(none=True)

    test = _TestSchema({'field': 'test', 'nullable_field': '123'})
    assert test.field == 'test' and test.nullable_field == '123'

    test = _TestSchema({'field': 'test', 'nullable_field': None})
    assert test.nullable_field == None

    with pytest.raises(oblate.ValidationError):
        _TestSchema({'field': None, 'nullable_field': '123'})

def test_required_fields():
    class _TestSchema(oblate.Schema):
        field = fields.String()
        optional_field = fields.String(required=False)
        default_optional_field = fields.String(default='default value')
        callable_default_optional_field = fields.String(default=lambda *_: 'callable default')  # type: ignore

    assert not _TestSchema.optional_field.has_default()
    assert _TestSchema.default_optional_field.has_default()

    test = _TestSchema({'field': 'test'})
    assert test.field == 'test'
    assert test.default_optional_field == _TestSchema.default_optional_field.default
    assert test.callable_default_optional_field == 'callable default'

    with pytest.raises(oblate.FieldNotSet):
        assert test.optional_field

    test = _TestSchema({
        'field': 'test',
        'optional_field': 'optional 1',
        'default_optional_field': 'optional 2',
    })
    assert test.optional_field == 'optional 1'
    assert test.default_optional_field == 'optional 2'

def test_field_copying():
    class _TestSchema(oblate.Schema):
        id = fields.Integer(strict=False)

    with pytest.raises(RuntimeError, match='bound'):
        class _TestSchemaField(oblate.Schema):  # type: ignore
            id = _TestSchema.id

    class _TestSchemaNew(oblate.Schema):
        id = _TestSchema.id.copy()

    assert _TestSchemaNew({'id': '1234'}).id == 1234

def test_field_data_keys():
    class _TestSchema(oblate.Schema):
        id = fields.Integer(data_key='Id')
        name = fields.String()

    schema = _TestSchema({'Id': 20, 'name': 'John'})

    assert schema.id == 20
    assert schema.dump()['Id'] == 20

    with pytest.raises(oblate.ValidationError, match='Invalid or unknown field'):
        _TestSchema({'id': 20, 'name': 'John'})

    assert schema.get_value_for('Id') == 20
    assert schema.get_value_for('id') == 20

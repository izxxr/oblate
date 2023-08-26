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

def test_schema_init():
    class _TestSchema(oblate.Schema):
        field = fields.String()

    test = _TestSchema({'field': 'test'})

    assert test.context.is_initialized()
    assert test.field == 'test'

    test.field = 'test 2'
    assert test.field == 'test 2'

    with pytest.raises(oblate.ValidationError, match='string'):
        test.field = 2  # type: ignore

    with pytest.raises(oblate.ValidationError, match='invalid'):
        _TestSchema({'invalid_field': 'test'})

def test_schema_dump():
    class _TestSchema(oblate.Schema):
        field = fields.String()
        field_2 = fields.String()
        field_3 = fields.String()
        field_4 = fields.String()

    data = {
        'field': 'test',
        'field_2': 'test 2',
        'field_3': 'test 3',
        'field_4': 'test 4',
    }
    partial_data = {'field_2': 'test 2', 'field_3': 'test 3'}
    test = _TestSchema(data)

    assert test.dump() == data
    assert test.dump(include=['field_2', 'field_3']) == partial_data
    assert test.dump(exclude=['field_4', 'field']) == partial_data

    with pytest.raises(TypeError):
        test.dump(include=[], exclude=[])

    class _TestField(fields.Field[Any, Any]):
        def value_load(self, value: Any, context: oblate.LoadContext) -> Any:
            return True

        def value_dump(self, value: Any, context: oblate.DumpContext) -> Any:
            raise ValueError('dump value error')

    class _TestSchemaErrorDump(oblate.Schema):
        field = _TestField()

    test = _TestSchemaErrorDump({'field': '1'})

    with pytest.raises(oblate.ValidationError, match='dump value error'):
        test.dump()


def test_get_value_for():
    class _TestSchema(oblate.Schema):
        field = fields.String()
        optional = fields.String(required=False)

    test = _TestSchema({'field': 'test'})
    assert test.get_value_for('field') == 'test'
    assert test.get_value_for('optional', 'default') == 'default'

    with pytest.raises(ValueError):
        test.get_value_for('optional')

    with pytest.raises(RuntimeError):
        test.get_value_for('invalid field')


def test_inheritance():
    class _Parent(oblate.Schema):
        parent_f = fields.Integer()
        parent_f2 = fields.Integer()

    class _Child(_Parent):
        child_f = fields.Integer()
        child_f2 = fields.Integer()

    class _SubChild(_Child):
        subchild_f = fields.Integer()

    parent_data = {'parent_f': 1, 'parent_f2': 2}
    child_data = {'child_f': 3, 'child_f2': 4}
    data = child_data.copy()
    data.update(parent_data)

    assert _Child(data).parent_f == 1
    assert _Child(data).child_f2 == 4

    data.update({'subchild_f': 5})

    assert _SubChild(data).child_f == 3
    assert _SubChild(data).subchild_f == 5

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
import typing as t
import pytest

def test_field_any():
    class _Schema(oblate.Schema):
        value = fields.Any()

    assert _Schema({'value': 1}).value == 1
    assert _Schema({'value': 'test'}).value == 'test'

    schema = _Schema({'value': 'raw'})
    assert schema.dump()['value'] == 'raw'


def test_field_literal():
    class _Schema(oblate.Schema):
        value = fields.Literal('test', 1, 3.14)

    assert _Schema({'value': 'test'}).value == 'test'
    assert _Schema({'value': 1}).value == 1
    assert _Schema({'value': 3.14}).value == 3.14

    sch = _Schema({'value': 'test'})
    assert sch.dump()['value'] == 'test'

    with pytest.raises(oblate.ValidationError, match="Value must be one of: 'test', 1, 3.14"):
        _Schema({'value': 'invalid'})

    class _SchemaEq(oblate.Schema):
        value = fields.Literal(2)

    with pytest.raises(oblate.ValidationError, match="Value must be 2"):
        _SchemaEq({'value': 'invalid'})

def test_field_union():
    class _Schema(oblate.Schema):
        value = fields.Union(str, bool)

    assert _Schema({'value': 'test'}).value == 'test'
    assert _Schema({'value': False}).value == False
    assert _Schema({'value': 'raw'}).dump()['value'] == 'raw'

    with pytest.raises(oblate.ValidationError, match=r"Type of 2 \(int\) is not compatible with types \(str, bool\)"):
        _Schema({'value': 2})

def test_field_type_expr():
    class _Schema(oblate.Schema):
        data = fields.TypeExpr(t.Tuple[t.Union[str, float], int])

    assert _Schema({'data': ('test', 3)}).data == ('test', 3)
    assert _Schema({'data': ('test', 3)}).dump()['data'] == ('test', 3)

    with pytest.raises(oblate.ValidationError, match='Tuple item at index 0'):
        _Schema({'data': (3, 3)})

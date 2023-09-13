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

def test_field_dict():
    class _Schema(oblate.Schema):
        data = fields.Dict()

    assert _Schema({'data': {}}).data == {}
    assert _Schema({'data': {'test': 1}}).data == {'test': 1}

    class _SchemaTyped(oblate.Schema):
        data = fields.Dict(str, t.Any)

    assert _SchemaTyped({'data': {'test': 1}}).data == {'test': 1}
    assert _SchemaTyped({'data': {'test': 1}}).dump()['data'] == {'test': 1}


    with pytest.raises(oblate.ValidationError, match='Dictionary key at index 0: Must be of type str'):
        _SchemaTyped({'data': {1: 1}})

    with pytest.raises(oblate.ValidationError, match='Value must be a dictionary'):
        _SchemaTyped({'data': 1})

def test_field_typed_dict():
    class Data(t.TypedDict):
        integer: int
        string: str
        maybe: t.NotRequired[str]

    class _Schema(oblate.Schema):
        data = fields.TypedDict(Data)

    assert _Schema({'data': {'integer': 2, 'string': 'test'}}).data['integer'] == 2
    assert _Schema({'data': {'integer': 2, 'string': 'test', 'maybe': 'test_2'}}).data['maybe'] == 'test_2'  # type: ignore
    assert _Schema({'data': {'integer': 2, 'string': 'test'}}).dump() == {'data': {'integer': 2, 'string': 'test'}}

    with pytest.raises(oblate.ValidationError, match="Value must be a dictionary"):
        _Schema({'data': 1})

    with pytest.raises(oblate.ValidationError, match="Validation failed for 'integer': Must be of type int"):
        _Schema({'data': {'integer': '2'}})

    with pytest.raises(oblate.ValidationError, match="Key 'string' is required"):
        _Schema({'data': {'integer': 2}})

    with pytest.raises(oblate.ValidationError, match="Invalid key 'invalid'"):
        _Schema({'data': {'invalid': 2}})

    class DataOptional(t.TypedDict, total=False):
        integer: int
        string: str
        maybe: t.NotRequired[str]

    class _SchemaOptional(oblate.Schema):
        data = fields.TypedDict(DataOptional)

    assert _SchemaOptional({'data': {}}).data == {}

    class DataOptionalReq(t.TypedDict, total=False):
        integer: int
        string: t.Required[str]

    class _SchemaOptionalReq(oblate.Schema):
        data = fields.TypedDict(DataOptionalReq)

    assert _SchemaOptionalReq({'data': {'string': 'text'}}).data['string'] == 'text'

    with pytest.raises(oblate.ValidationError, match="Key 'string' is required"):
        _SchemaOptionalReq({'data': {'integer': 2}})

def test_field_list():
    class _Schema(oblate.Schema):
        untyped = fields.List()
        typed = fields.List(t.Union[str, int])

    sch = _Schema({'untyped': [1, 2, '3', 4.0], 'typed': [1, 2, '3']})
    assert sch.untyped == [1, 2, '3', 4.0]
    assert sch.typed == [1, 2, '3']
    assert sch.dump() == {'untyped': [1, 2, '3', 4.0], 'typed': [1, 2, '3']}

    with pytest.raises(oblate.ValidationError, match="Value must be a list"):
        _Schema({'untyped': 1})

    with pytest.raises(oblate.ValidationError, match=r"Sequence item at index 1: Type of 3.14 \(float\) is not compatible with types \(str, int\)"):
        _Schema({'untyped': [1, 2, 3], 'typed': [1, 3.14, '2']})

def test_field_set():
    class _Schema(oblate.Schema):
        untyped = fields.Set()
        typed = fields.Set(t.Union[str, int])

    sch = _Schema({'untyped': {1, 2, '3', 4.0}, 'typed': {1, 2, '3'}})
    assert sch.untyped == {1, 2, '3', 4.0}
    assert sch.typed == {1, 2, '3'}
    assert sch.dump() == {'untyped': {1, 2, '3', 4.0}, 'typed': {1, 2, '3'}}

    with pytest.raises(oblate.ValidationError, match="Value must be a set"):
        _Schema({'untyped': [1]})

    with pytest.raises(oblate.ValidationError,
                       match=r"Set includes an invalid item: Type of 3.14 \(float\) is not compatible with types \(str, int\)"):
        _Schema({'untyped': {1, 2, 3}, 'typed': {1, '2', 3.14}})

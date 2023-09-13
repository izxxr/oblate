# # MIT License

# # Copyright (c) 2023 Izhar Ahmad

# # Permission is hereby granted, free of charge, to any person obtaining a copy
# # of this software and associated documentation files (the "Software"), to deal
# # in the Software without restriction, including without limitation the rights
# # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# # copies of the Software, and to permit persons to whom the Software is
# # furnished to do so, subject to the following conditions:

# # The above copyright notice and this permission notice shall be included in all
# # copies or substantial portions of the Software.

# # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# # SOFTWARE.

from __future__ import annotations

import oblate
import pytest
import typing as t

if t.TYPE_CHECKING:
    class _Schema(oblate.Schema):
        t: oblate.fields.TypeExpr[t.Any]

def _make_schema_from_expr(expr: t.Any) -> t.Type[_Schema]:
    class _Schema(oblate.Schema):
        t = oblate.fields.TypeExpr(expr)

    return _Schema

def test_union():
    schema = _make_schema_from_expr(t.Union[str, int])
    assert schema(dict(t='text')).t == 'text'
    assert schema(dict(t=1)).t == 1

    with pytest.raises(oblate.ValidationError, match=r'Type of 3.14 \(float\) is not compatible with types \(str, int\)'):
        schema(dict(t=3.14))

def test_literal():
    schema = _make_schema_from_expr(t.Literal['owner', 'admin', 'member'])
    assert schema(dict(t='owner')).t == 'owner'
    assert schema(dict(t='admin')).t == 'admin'
    assert schema(dict(t='member')).t == 'member'

    with pytest.raises(oblate.ValidationError, match=r"Value must be one of: 'owner', 'admin', 'member'"):
        schema(dict(t='test'))

def test_any():
    schema = _make_schema_from_expr(t.Any)
    assert schema(dict(t='text')).t == 'text'
    assert schema(dict(t=1)).t == 1
    assert schema(dict(t=3.14)).t == 3.14

def test_sequence():
    schema = _make_schema_from_expr(t.Sequence[str])
    assert schema(dict(t=['t', 't2', 't3'])).t == ['t', 't2', 't3']
    assert schema(dict(t=('t', 't2', 't3'))).t == ('t', 't2', 't3')
    assert schema(dict(t={'t', 't2', 't3'})).t

    with pytest.raises(oblate.ValidationError, match=r"Sequence item at index 2: Must be of type str"):
        schema(dict(t=['t', 't2', 3]))

def test_list():
    schema = _make_schema_from_expr(t.List[str])
    assert schema(dict(t=['t', 't2', 't3'])).t == ['t', 't2', 't3']

    with pytest.raises(oblate.ValidationError, match=r"Sequence item at index 2: Must be of type str"):
        schema(dict(t=['t', 't2', 3]))

    with pytest.raises(oblate.ValidationError, match=r"Must be a valid list"):
        schema(dict(t=('t', 't2', 't')))

def test_set():
    schema = _make_schema_from_expr(t.Set[str])
    assert schema(dict(t={'t', 't2', 't3'})).t == {'t', 't2', 't3'}

    with pytest.raises(oblate.ValidationError, match=r"Set includes an invalid item: Must be of type str"):
        schema(dict(t={'t', 't2', 3}))

    with pytest.raises(oblate.ValidationError, match=r"Must be a valid set"):
        schema(dict(t=('t', 't2', 't')))

def test_tuple():
    schema = _make_schema_from_expr(t.Tuple[str, int, float])
    assert schema(dict(t=('t', 2, 3.14))).t == ('t', 2, 3.14)

    with pytest.raises(oblate.ValidationError, match=r"Tuple item at index 1: Must be of type int"):
        schema(dict(t=('t', 2.12, 2.3)))

    with pytest.raises(oblate.ValidationError, match=r"Tuple length must be 3 \(current length: 2\)"):
        schema(dict(t=('t', 2)))

    with pytest.raises(oblate.ValidationError, match=r"Must be a valid tuple"):
        schema(dict(t={'t', 't2', 't'}))

    schema_var_length = _make_schema_from_expr(t.Tuple[int, ...])
    assert schema_var_length(dict(t=(1, 2, 3, 4, 5))).t == (1, 2, 3, 4, 5)

    with pytest.raises(oblate.ValidationError, match=r"Tuple item at index 3: Must be of type int"):
        schema_var_length(dict(t=(1, 2, 3, '4', 5)))

def test_dict():
    schema = _make_schema_from_expr(t.Dict[str, int])
    assert schema(dict(t={'t': 1})).t == {'t': 1}

    with pytest.raises(oblate.ValidationError, match=r"Dictionary value for key 't': Must be of type int"):
        schema(dict(t={'t': '1'}))

    with pytest.raises(oblate.ValidationError, match=r"Dictionary key at index 0: Must be of type str"):
        schema(dict(t={1: '1'}))

    with pytest.raises(oblate.ValidationError, match=r"Must be a valid dictionary"):
        schema(dict(t={'t', 't2', 't'}))

def test_unknown():
    schema = _make_schema_from_expr(t.Type[int])
    assert schema(dict(t={'t': 1})).t == {'t': 1}

def test_typed_dict():
    # mostly covered in test_fields_struct.test_typed_dict
    class Data(t.TypedDict):
        test: str

    schema = _make_schema_from_expr(Data)
    assert schema({'t': {'test': '2'}}).t == {'test': '2'}

    with pytest.raises(oblate.ValidationError):
        schema({'t': {'test': 2}})

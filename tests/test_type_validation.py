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


def _test_validate_types(types: t.Mapping[str, type], values: t.Mapping[str, t.Any], error: t.Optional[str]):
    if not error:
        return oblate.validate_types(types, values)

    with pytest.raises(oblate.TypeValidationError) as exc_info:
        oblate.validate_types(types, values)

    assert exc_info.value.errors['root'][0] == error


ERR_UNION = 'Type of {value} ({type}) is not compatible with types ({types})'
ERR_LITERAL_MULTIPLE = 'Value must be one of: {values}'
ERR_LITERAL_SINGLE = 'Value must be equal to {value}'
ERR_SEQUENCE_ELEM = 'Sequence item at index {index}: Must be of type {type}'
ERR_LIST_ELEM = ERR_SEQUENCE_ELEM
ERR_LIST_TYPE = 'Must be a valid list'
ERR_SET_ELEM = 'Set includes an invalid item: Must be of type {type}'
ERR_SET_TYPE = 'Must be a valid set'
ERR_TUPLE_ELEM = 'Tuple item at index {index}: Must be of type {type}'
ERR_TUPLE_LENGTH = 'Tuple length must be {length} (current length: {current})'
ERR_TUPLE_TYPE = 'Must be a valid tuple'
ERR_DICT_KEY = 'Dictionary key at index {index}: Must be of type {type}'
ERR_DICT_VALUE = 'Dictionary value for key \'{key}\': Must be of type {type}'
ERR_DICT_TYPE = 'Must be a valid dictionary'

def test_missing_keys():
    types = {
        'name': str,
        'id': t.Union[int, str]
    }

    with pytest.raises(oblate.TypeValidationError) as exc_info:
        oblate.validate_types(types, {'name': 'John'})

    assert exc_info.value.errors['id'][0] == 'This key is missing.'
    oblate.validate_types(types, {'name': 'John'}, ignore_missing=True)

def test_extra_keys():
    types = {
        'name': str,
    }

    with pytest.raises(oblate.TypeValidationError) as exc_info:
        oblate.validate_types(types, {'name': 'John', 'id': 'test'})

    assert exc_info.value.errors['id'][0] == "Invalid key"
    oblate.validate_types(types, {'name': 'John', 'id': 'test'}, ignore_extra=True)


@pytest.mark.parametrize(
        ['types', 'values', 'error'],
        [
            (dict(root=t.Union[str, int]), dict(root='test'), None),
            (dict(root=t.Union[str, int]), dict(root=1), None),
            (dict(root=t.Union[str, int]), dict(root=3.14),
             ERR_UNION.format(value=3.14, type='float', types='str, int')),
        ]
)
def test_union(types: t.Mapping[str, type], values: t.Mapping[str, t.Any], error: t.Optional[str]):
    _test_validate_types(types, values, error)

@pytest.mark.parametrize(
        ['types', 'values', 'error'],
        [
            (dict(root=t.Literal['owner', 'admin']), dict(root='owner'), None),
            (dict(root=t.Literal['owner', 'admin']), dict(root='admin'), None),
            (dict(root=t.Literal['owner', 'admin']), dict(root='test'),
             ERR_LITERAL_MULTIPLE.format(value='test', values="'owner', 'admin'")),
            (dict(root=t.Literal['owner']), dict(root='admin'),
             ERR_LITERAL_SINGLE.format(value="'owner'")),
        ]
)
def test_literal(types: t.Mapping[str, type], values: t.Mapping[str, t.Any], error: t.Optional[str]):
    _test_validate_types(types, values, error)

@pytest.mark.parametrize(
        ['types', 'values', 'error'],
        [
            (dict(root=t.Any), dict(root='test'), None),
            (dict(root=t.Any), dict(root=3.14), None),
            (dict(root=t.Any), dict(root=1), None),
        ]
)
def test_any(types: t.Mapping[str, type], values: t.Mapping[str, t.Any], error: t.Optional[str]):
    _test_validate_types(types, values, error)

@pytest.mark.parametrize(
        ['types', 'values', 'error'],
        [
            (dict(root=t.Sequence[str]), dict(root=['t', 't2', 't3']), None),
            (dict(root=t.Sequence[str]), dict(root=('t', 't2', 't3')), None),
            (dict(root=t.Sequence[str]), dict(root={'t', 't2', 't3'}), None),
            (dict(root=t.Sequence[str]), dict(root=['t', 't2', 3]),
             ERR_SEQUENCE_ELEM.format(index=2, type='str')),
        ]
)
def test_sequence(types: t.Mapping[str, type], values: t.Mapping[str, t.Any], error: t.Optional[str]):
    _test_validate_types(types, values, error)

@pytest.mark.parametrize(
        ['types', 'values', 'error'],
        [
            (dict(root=t.List[str]), dict(root=['t', 't2', 't3']), None),
            (dict(root=t.List[str]), dict(root=('t', 't2', 't3')), ERR_LIST_TYPE),
            (dict(root=t.List[str]), dict(root=['t', 't2', 3]),
             ERR_LIST_ELEM.format(index=2, type='str')),
        ]
)
def test_list(types: t.Mapping[str, type], values: t.Mapping[str, t.Any], error: t.Optional[str]):
    _test_validate_types(types, values, error)

@pytest.mark.parametrize(
        ['types', 'values', 'error'],
        [
            (dict(root=t.Set[str]), dict(root={'t', 't2', 't3'}), None),
            (dict(root=t.Set[str]), dict(root=('t', 't2', 't')), ERR_SET_TYPE),
            (dict(root=t.Set[str]), dict(root={'t', 't2', 3}),
             ERR_SET_ELEM.format(type='str')),
        ]
)
def test_set(types: t.Mapping[str, type], values: t.Mapping[str, t.Any], error: t.Optional[str]):
    _test_validate_types(types, values, error)

@pytest.mark.parametrize(
        ['types', 'values', 'error'],
        [
            (dict(root=t.Tuple[str, int, float]), dict(root=('t', 2, 3.14)), None),
            (dict(root=t.Tuple[str, int, float]), dict(root={'t', 't2', 't'}), ERR_TUPLE_TYPE),
            (dict(root=t.Tuple[str, int, float]), dict(root=('t', 2.12, 2.3)),
             ERR_TUPLE_ELEM.format(index='1', type='int')),
            (dict(root=t.Tuple[str, int, float]), dict(root=('t', 2)),
             ERR_TUPLE_LENGTH.format(length='3', current='2')),
            (dict(root=t.Tuple[int, ...]), dict(root=(1, 2, 3, 4, 5)), None),
            (dict(root=t.Tuple[int, ...]), dict(root=(1, 2, 3, '4', 5)),
             ERR_TUPLE_ELEM.format(index='3', type='int')),
        ]
)
def test_tuple(types: t.Mapping[str, type], values: t.Mapping[str, t.Any], error: t.Optional[str]):
    _test_validate_types(types, values, error)

@pytest.mark.parametrize(
        ['types', 'values', 'error'],
        [
            (dict(root=t.Dict[str, int]), dict(root={'t': 1}), None),
            (dict(root=t.Dict[str, int]), dict(root={'t', 't2', 't'}), ERR_DICT_TYPE),
            (dict(root=t.Dict[str, int]), dict(root={'t': '1'}),
             ERR_DICT_VALUE.format(key='t', type='int')),
            (dict(root=t.Dict[str, int]), dict(root={1: 1}),
             ERR_DICT_KEY.format(index=0, type='str')),
        ]
)
def test_dict(types: t.Mapping[str, type], values: t.Mapping[str, t.Any], error: t.Optional[str]):
    _test_validate_types(types, values, error)

@pytest.mark.parametrize(
        ['types', 'values', 'error'],
        [(dict(root=t.Type[int]), dict(root={'t': 1}), None)]
)
def test_unknown(types: t.Mapping[str, type], values: t.Mapping[str, t.Any], error: t.Optional[str]):
    _test_validate_types(types, values, error)


def test_typed_dict():
    # mostly covered in test_fields_struct.test_typed_dict
    class Data(t.TypedDict):
        test: str

    types = {'data': Data}
    oblate.validate_types(types, {'data': {'test': '2'}})

    with pytest.raises(oblate.TypeValidationError):
        oblate.validate_types(types, {'data': {'test': 2}})

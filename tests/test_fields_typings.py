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

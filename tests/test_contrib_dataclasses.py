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
from oblate.contrib.dataclasses import create_schema_cls
from dataclasses import field, dataclass

import oblate
import pytest

def test_dataclasses_basic():
    @dataclass
    class User:
        id: int
        username: str
        is_employee: bool = False

    UserSchema = create_schema_cls(User)
    sch = UserSchema({'id': 2, 'username': 'John'})

    assert sch.id == 2  # type: ignore
    assert sch.is_employee == False  # type: ignore
    assert UserSchema({'id': 2, 'username': 'John', 'is_employee': True}).is_employee == True  # type: ignore

    with pytest.raises(oblate.ValidationError, match='This field is required'):
        UserSchema({'id': 2})


class _TestCls:
    ...


def test_dataclasses_unknown_type():
    @dataclass
    class Test:
        test: _TestCls

    TestSchema = create_schema_cls(Test)
    assert TestSchema({'test': _TestCls()})

    with pytest.raises(oblate.ValidationError, match='Must be of type _TestCls'):
        TestSchema({'test': 2})

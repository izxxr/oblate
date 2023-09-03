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

from typing import Any, Union
from oblate import fields

import pytest
import oblate

def test_error_field_binding():
    class _TestField(fields.Field[Any, Any]):
        def value_load(self, value: Any, context: oblate.LoadContext) -> Any:
            err = oblate.FieldError('test message')
            assert err.field == self
            return context.value

    class _TestSchema(oblate.Schema):
        field_1 = _TestField()
        field_2 = fields.String()
        field_3 = fields.String()

    try:
        _TestSchema({
            'field_1': '1',
            'field_2': 2,
            'field_3': 3,
        })
    except oblate.ValidationError as err:
        for error in err.errors:
            assert error.field == error.field
            assert error.key == f'field_{error.context.value}'  # type: ignore

def test_standard_errors():
    class _TestFieldAssertionError(fields.Field[Any, Any]):
        ERROR_MESSAGE = 'assert'

        def value_load(self, value: Any, context: oblate.LoadContext) -> Any:
            raise AssertionError(self.ERROR_MESSAGE)

    class _TestFieldValueError(fields.Field[Any, Any]):
        ERROR_MESSAGE = 'value'

        def value_load(self, value: Any, context: oblate.LoadContext) -> Any:
            raise ValueError(self.ERROR_MESSAGE)

    class _TestSchema(oblate.Schema):
        assertion_error = _TestFieldAssertionError()
        value_error = _TestFieldValueError()

    try:
        _TestSchema({'assertion_error': '1', 'value_error': '2'})
    except oblate.ValidationError as err:
        for error in err.errors:
            assert isinstance(error, oblate.FieldError)
            if error.field == _TestSchema.assertion_error:
                assert error.message == _TestFieldAssertionError.ERROR_MESSAGE
            else:
                assert error.message == _TestFieldValueError.ERROR_MESSAGE


def test_error_raw():
    class _TestSchema(oblate.Schema):
        integer = fields.Integer(strict=False)
        string = fields.String()

    try:
        _TestSchema({'integer': 'invalid int', 'string': 'test'})
    except oblate.ValidationError as err:
        raw = err.raw()
        assert raw.pop('integer')
        assert not raw


def test_field_format_error():
    class Int(fields.Integer):
        def format_error(self, error_code: Any, context: oblate.ErrorContext) -> Union[oblate.FieldError, str]:
            if error_code == self.ERR_INVALID_DATATYPE:
                return oblate.FieldError('Invalid datatype, must be string')
            if error_code == self.ERR_COERCION_FAILED:
                return f'Coercion to integer failed for {context.get_value()}'

            return super().format_error(error_code, context)

    class _TestSchema(oblate.Schema):
        integer = Int()

    class _TestSchemaNoStrict(oblate.Schema):
        integer = Int(strict=False)

    with pytest.raises(oblate.ValidationError, match='Invalid datatype, must be string'):
        _TestSchema({'integer': 'invalid'})

    with pytest.raises(oblate.ValidationError, match='Coercion to integer failed for invalid'):
        _TestSchemaNoStrict({'integer': 'invalid'})

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

import oblate
import pytest


def test_global_config():
    assert oblate.GlobalConfig.validation_error_cls == oblate.ValidationError

    with pytest.raises(TypeError, match='subclass'):
        oblate.config.validation_error_cls = int  # type: ignore

    class CustomValidationError(oblate.ValidationError): ...

    oblate.config.validation_error_cls = CustomValidationError
    assert oblate.GlobalConfig.validation_error_cls == oblate.ValidationError
    assert oblate.config.validation_error_cls == CustomValidationError

    oblate.config = oblate.GlobalConfig(validation_error_cls=CustomValidationError)
    assert oblate.config.validation_error_cls == CustomValidationError

    with pytest.raises(TypeError, match='Invalid config'):
        oblate.GlobalConfig(invalid_cfg=None)

    oblate.config = oblate.GlobalConfig()
    assert oblate.config.validation_error_cls == oblate.ValidationError


def test_schema_config():
    class _SchemaNoConfig(oblate.Schema):
        ...

    class _Schema(oblate.Schema):
        class Config(oblate.SchemaConfig):
            ...

    assert _Schema.__config__ == _Schema.Config
    assert _SchemaNoConfig.__config__ == oblate.SchemaConfig

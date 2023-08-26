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


def test_global_config_validation_error_cls():
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


def test_schema_config_add_repr():
    class _SchemaDefault(oblate.Schema):
        ...

    class _SchemaRepr(oblate.Schema):
        class Config(oblate.SchemaConfig):
            add_repr = True

    class _SchemaNoRepr(oblate.Schema):
        class Config(oblate.SchemaConfig):
            add_repr = False

    assert repr(_SchemaDefault({})) == ('_SchemaDefault()')
    assert repr(_SchemaRepr({})) == ('_SchemaRepr()')
    assert repr(_SchemaNoRepr({})) != ('_SchemaNoRepr()')

def test_schema_config_slotted():
    class _SchemaDefault(oblate.Schema):
        ...

    class _SchemaSlots(oblate.Schema):
        class Config(oblate.SchemaConfig):
            slotted = True

    class _SchemaNoSlots(oblate.Schema):
        class Config(oblate.SchemaConfig):
            slotted = False

    with pytest.raises(AttributeError, match="object has no attribute 'test'"):
        _SchemaDefault({}).test = None  # type: ignore

    with pytest.raises(AttributeError, match="object has no attribute 'test'"):
        _SchemaSlots({}).test = None  # type: ignore

    schema = _SchemaNoSlots({})
    schema.test = None  # type: ignore
    assert schema.test == None  # type: ignore


def test_inherited_config():
    class Base(oblate.Schema):
        class Config(oblate.SchemaConfig): ...

    class Child(Base): ...
    class Override(Base):
        class NewConfig(oblate.SchemaConfig): ...

    assert Base.__config__ == Base.Config
    assert Child.__config__ == Base.Config
    assert Override.__config__ == Override.NewConfig


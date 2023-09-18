"""
oblate.contrib.dataclasses
~~~~~~~~~~~~~~~~~~~~~~~~~~

Support for integration of Oblate schemas with standard dataclasses.

The main component of this package is the :func:`.create_schema_cls`
function used to create a :class:`oblate.Schema` class type from a
data class.

This function takes a dataclass as parameter and returns the formed
:class:`Schema` subclass. Each attribute of the dataclass is automatically
mapped to the respective Oblate field. Following set of considerations
are taken into account when mapping types to respective fields:

- For primitive types (e.g. str, int, bool etc.), the type is simply mapped
  to the relevant field.

- For data structures, the type is mapped to relevant field and any type
  arguments passed to the data structure are also passed to the field for
  type validation. See the :ref:`data structures fields <guide-fields-data-structures>`
  section in the guide for more information.

- The types from ``typing`` module that can be mapped to a relevant field
  are mapped to that field otherwise these types are directly passed to the
  :class:`oblate.fields.TypeExpr` field. See :ref:`guide-type-validation`
  for more information.

- Types that cannot be mapped to a specific field or are not supported are
  directly passed to the :class:`oblate.fields.TypeExpr` field which performs
  further validation for it. See :ref:`guide-type-validation` for more
  information.

- The ``default`` parameter in a field is automatically set on the basis
  of whether the field has a default set in dataclass.

- The ``none`` parameter in a field is automatically set if :class:`typing.Optional`
  or ``T | None`` is used.

- A dict can be passed to ``oblate_field_kwargs`` key in ``metadata`` mapping
  in a dataclass field. That dictionary is passed as keyword arguments to the
  field. Note that if this dictionary includes parameters that are normally
  handled transparently e.g. ``default`` or ``none`` etc. then no internal
  handling is done for these parameters and they are passed as-is to the field.
  This means if ``oblate_field_kwargs`` is ``{'none': False}`` but field is marked as
  ``Optional``, the ``none`` parameter is still passed as ``False``.

Copyright (C) Izhar Ahmad 2023-present.
This project is under the MIT license, see LICENSE for more information.
"""
from __future__ import annotations

import typing as t
import types
import oblate
import dataclasses

__author__  = 'Izhar Ahmad (izxxr)'
__all__ = (
    'create_schema_cls',
)


_type_field_map: t.Dict[type, t.Type[oblate.fields.Field[t.Any, t.Any]]] = {
    str: oblate.fields.String,
    int: oblate.fields.Integer,
    float: oblate.fields.Float,
    bool: oblate.fields.Boolean,
    list: oblate.fields.List,
    set: oblate.fields.Set,
    dict: oblate.fields.Dict,
    t.Any: oblate.fields.Any,
    t.Literal: oblate.fields.Literal,
    t.Union: oblate.fields.Union,
}

_NoneType = type(None)

def _get_field_kwargs(field: dataclasses.Field[t.Any]):
    kwargs: t.Dict[str, t.Any] = field.metadata.get('oblate_field_kwargs', {})
    if field.default is not dataclasses.MISSING:
        kwargs.setdefault('default', field.default)
    return kwargs

def _resolve_field(field: dataclasses.Field[t.Any], annotations: t.Dict[str, t.Any]):
    kwargs = _get_field_kwargs(field)
    args: t.List[t.Any] = []

    tp = annotations.get(field.name, field.type)
    if isinstance(tp, str):
        raise TypeError(f'failed to resolve type {tp!r}')  # pragma: no cover

    origin = t.get_origin(tp)
    targs = list(t.get_args(tp))

    if origin is not None:
        if origin in (t.Union, types.UnionType) and _NoneType in targs:
            if kwargs.setdefault('none', True):
                targs.remove(_NoneType)
        if origin in _type_field_map:
            field_tp = _type_field_map[origin]
            args.extend(targs)
        else:
            field_tp = oblate.fields.TypeExpr
            args.extend(tp)
    else:
        field_tp = _type_field_map.get(tp)
        if field_tp is None:
            # unsupported, fallback to TypeExpr
            field_tp = oblate.fields.TypeExpr
            args.append(tp)
    return field_tp(*args, **kwargs)

def create_schema_cls(dataclass: type) -> t.Type[oblate.Schema]:
    """Creates a :class:`Schema` using a standard dataclass.

    For more information on how this function performs the conversion,
    see the package documentation.

    Parameters
    ----------
    dataclass: :class:`type`
        The dataclass to convert into schema.

    Returns
    -------
    :class:`Schema`
        The schema being converted.
    """
    if not dataclasses.is_dataclass(dataclass):
        raise TypeError('The argument to create_schema_cls() must be a dataclass')  # pragma: no cover

    attrs: t.Dict[str, t.Any] = {}
    annotations = t.get_type_hints(dataclass)

    for field in dataclasses.fields(dataclass):
        attrs[field.name] = _resolve_field(field, annotations)

    return type(dataclass.__qualname__, (oblate.Schema,), attrs)

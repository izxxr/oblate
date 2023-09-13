.. currentmodule:: oblate

Changelog
=========

This page has changelogs for all releases of Oblate.

v1.1.0
------

New features
~~~~~~~~~~~~

- Add :class:`fields.List` for accepting :class:`list` structure.
- Add :class:`fields.Set` for accepting :class:`set` structures.
- Add :class:`fields.Dict` and :class:`fields.TypedDict` for handling dictionaries.
- Add :class:`fields.TypeExpr` for validating types using simple type expressions.
- Add :class:`fields.Any` field as a no validation field.
- Add :class:`fields.Literal` field to accept pre-defined literal values.
- Add :class:`fields.Union` for basic union type validation.
- Add :class:`validate.Range` validator for validating integer ranges.
- Add :class:`validate.Length` validator for validating length of sized types.
- Add :class:`validate.Regex` validator for validating values using regular expression.
- Add :class:`validate.Exclude` validator for disallowing/excluding specific values.
- Add :class:`validate.Or` validator for OR'ing the result of multiple validators.
- Add :meth:`Schema.__schema_post_init__` method as a post initialization hook.
- Add :class:`ErrorContext.metadata` for storing extra error information.
- Add :attr:`GlobalConfig.warn_unsupported_types` to control behaviour on using unsupported types.
- Add :attr:`Field.name` and :attr:`Field.schema` properties.
- Add ``init_kwargs`` parameter in :class:`fields.Object` to support passing initialization arguments.

Improvements
~~~~~~~~~~~~

- :class:`fields.Object` field now supports passing :class:`Schema` instances directly instead of raw data.
- :meth:`fields.Field.format_error` no longer requires super call and default error messages are resolved automatically.

v1.0.0
------

This version brings an entire rewrite of the library. Many features have been removed along with
many additions and breaking changes. 0.2.0 and former are not compatible with this version.

For an overview of changes, see `this pull request <https://github.com/izxxr/oblate/pulls/3>`_.

v0.2.0
------

New features
~~~~~~~~~~~~

- Add support for partial schemas
    - Add :class:`fields.Partial` field.
    - Add :meth:`Schema.is_partial` helper method.

- Add :meth:`ValidationError.is_field_error` helper to check whether exception relates to a field.
- Add :meth:`Schema.after_init_hook` method that gets called when schema is finished initializing.
- Add ``load_key`` and ``dump_key`` parameters to :class:`fields.Field` to control the field names
  during serialization/deserialization of data.
- Add :attr:`ValidationError.state` to allow storing state to an error that can later be accessed.
- Add ``include`` and ``exclude`` parameters to :meth:`Schema.dump`.
- Add ``raw`` parameter to :meth:`Field.validate` and :meth:`Field.add_validator` to validate
  raw value.

Improvements
~~~~~~~~~~~~

- :class:`~fields.Object` fields now support raw data serialization upon setting after initialization.
- :class:`Schema` and all fields now have ``__slots__`` defined for performance sake.
- User defined validators are now ran after field ``value_*`` methods by default. Such that,
  validators now take serialized value instead of raw one. For previous behaviour, ``raw``
  parameter must be used.

Bug fixes
~~~~~~~~~

- Fix :meth:`Schema.dump` returning empty dictionary.
- Fix fields returning improper values when initializing multiple schemas.
- Fix unable to set ``None`` on nullable fields after initialization.
- Fix field getting the new value using the setter even when the validations fail.

Documentation
~~~~~~~~~~~~~

- Add "Tutorials" section

v0.1.0
------

- Initial release

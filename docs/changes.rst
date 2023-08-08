.. currentmodule:: oblate

Changelog
=========

This page has changelogs for all releases of Oblate.

v0.3.0
------

New features
~~~~~~~~~~~~

- Add the :attr:`fields.Field.raw_validators` property to access the list of raw validators associated
  to a field.


Bug fixes
~~~~~~~~~

- Fix :meth:`Schema.value_load` getting called instead of :meth:`Schema.value_set` during 
  initialization.


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

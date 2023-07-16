.. currentmodule:: oblate

Changelog
=========

This page has changelogs for all releases of Oblate.

v0.2.0
------

- Add support for partial schemas
    - Add :class:`fields.Partial` field.
    - Add :meth:`Schema.is_partial` helper method.

- Add :meth:`ValidationError.is_field_error` helper to check whether exception relates to a field.
- Add :meth:`Schema.after_init_hook` method that gets called when schema is finished initializing.
- Add ``load_key`` and ``dump_key`` parameters to :class:`fields.Field` to control the field names
  during serialization/deserialization of data.

- :class:`~fields.Object` fields now support raw data serialization upon setting after initialization.
- :class:`Schema` and all fields now have ``__slots__`` defined for performance sake.

- Fix :meth:`Schema.dump` returning empty dictionary.

v0.1.0
------

- Initial release

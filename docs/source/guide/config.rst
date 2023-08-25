.. currentmodule:: oblate
.. _guide-config:

Configuration
=============

Oblate provides an interface that can be customized to suit all use cases. This page covers the topic
of working with various configurations.

.. _guide-config-schema-config:

Schema configuration
--------------------

The :class:`SchemaConfig` is used for defining per-schema configuration. Schema configuration is used
to customize the behaviour of a specific :class:`Schema`.

In order to do so, a nested class is added inside a :class:`Schema` subclass that inherits from the
:class:`SchemaConfig` class. This class will have class variables to define the configuration options::

    class User(oblate.Schema):
        ...  # fields here

        class Config(oblate.SchemaConfig):
            add_repr = False

In this case, ``User.Config`` class defines the configuration for ``User`` schema. ``add_repr`` is
overriden to ``False``. Other configuration options are also added as class variables.

.. _guide-config-global-config:

Global configuration
--------------------

Apart from schema configuration, Oblate also have some global configuration options. Global
configuration is used for configuration features that are not specific to a schema. These
options apply globally rather than for a specific schema.

Global configuration is handled by :data:`oblate.config` which is a :class:`GlobalConfig` instance.
Various attributes on this instance can be changed to update global configuration.

For example, changing the default :class:`ValidationError` exception to raise::

    oblate.config.validator_error_cls = MyCustomError

    # -- OR --

    oblate.config = oblate.GlobalConfig(validation_error_cls=MyCustomError)

More information
----------------

To get information about configuration options, see their relevant guide pages. For list of all
available configuration attributes, see the :ref:`api-config` API reference.

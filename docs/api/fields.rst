.. currentmodule:: oblate

Fields
======

Fields are used to define the attributes of a schema. Oblate provides built in support for
commonly used fields as well as provides the ability to user to create custom fields.

Base class
----------

.. autoclass:: oblate.fields.Field
    :members:

Primitive data types
--------------------

The fields below are for basic primitive data types.

BasePrimitiveField
~~~~~~~~~~~~~~~~~~

.. autoclass:: oblate.fields.BasePrimitiveField
    :members:

String
~~~~~~

.. autoclass:: oblate.fields.String
    :members:

Integer
~~~~~~~

.. autoclass:: oblate.fields.Integer
    :members:

Float
~~~~~

.. autoclass:: oblate.fields.Float
    :members:

Boolean
~~~~~~~

.. autoclass:: oblate.fields.Boolean
    :members:

Nesting schemas
---------------

These fields allow you to nest schemas inside schemas.

Object
~~~~~~

.. autoclass:: oblate.fields.Object
    :members:

Partial
~~~~~~~

.. autoclass:: oblate.fields.Partial
    :members:

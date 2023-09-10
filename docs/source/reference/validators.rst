.. currentmodule:: oblate
.. _api-validators:

Validators
==========

The :mod:`oblate.validate` module provides some built-in commonly used validators and also provides the
utilities to define your own validators.

Field Validator
---------------

.. autofunction:: oblate.validate.field

Base class
----------

.. autoclass:: oblate.validate.Validator
    :members:

.. _api-validators-prebuilt-validators:

Prebuilt Validators
-------------------

.. autoclass:: oblate.validate.Range
    :members:

.. autoclass:: oblate.validate.Length
    :members:

.. autoclass:: oblate.validate.Exclude
    :members:

.. autoclass:: oblate.validate.Or
    :members:

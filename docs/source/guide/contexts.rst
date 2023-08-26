.. currentmodule:: oblate
.. _guide-contexts:

Contexts
========

This page covers all about the purpose and working of :ref:`api-contexts`.

Introduction
------------

Context objects are classes meant to hold useful contextual data about some event. These classes are
passed by library in user side functions and methods.

Schema Context
--------------

:class:`SchemaContext` is accessed by :attr:`Schema.context` attribute. This class stores information
about a schema and its state.

Field Contexts
--------------

When a field is being processed, some contextual information is required to be passed to user side
function and methods. This is done by field contexts.

There are two field contexts:

- :class:`LoadContext` when a field is being loaded (serialized)
- :class:`DumpContext` when a field is being dumped (deserialized)

:class:`LoadContext` is passed to methods and functions involved in serialization of fields such
as :meth:`fields.Field.value_load` and validators while :class:`DumpContext` is passed to
:meth:`fields.Field.value_dump`.

Context States
--------------

All contexts provided by the library have a ``state`` attribute which is a dictionary. This attribute
exists to allow users to easily propagate or store important state information in the context and
access it later at some point.

A common use case of ``state`` is when loading a field. The :meth:`fields.Field.value_load` method
can store some data in state which validators can access.

Another use case is preserving the raw value of some field to access it later during the
deserialization of field. Example of this use case is given below::

    class SumValues(fields.Field[list[int], int]):
        def value_load(self, value: list[int], ctx: oblate.LoadContext) -> int:
            if not isinstance(value, list):
                raise ValueError('Value for this field must be a list of integers')

            result = 0
            for idx, num in enumerate(value):
                if not isinstance(num, int):
                    raise ValueError(f'Non-integer value at index {idx}')

                result += num

            ctx.schema.context.state['marks_raw_value'] = value
            return result

        def value_dump(self, value: int, ctx: oblate.DumpContext) -> list[int]:
            return ctx.schema.context.state['marks_raw_value']

    class Student(oblate.Schema):
        name = fields.String()
        test_score = SumValues()

    std = Student({'name': 'John', 'test_score': [10, 9, 5, 6]})
    print(std.test_score)  # 30

    print(std.dump()['test_score'])  # [10, 9, 5, 6]

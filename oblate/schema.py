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

from typing import Dict, Any, Mapping, List, Optional, Sequence, Tuple
from oblate.fields.base import Field
from oblate.contexts import SchemaContext, LoadContext, DumpContext
from oblate.utils import MISSING, current_field_name, current_context, current_schema
from oblate.exceptions import FieldError, ValidationError

__all__ = (
    'Schema',
)


class Schema:
    """The base class for all schemas."""
    __fields__: Dict[str, Field[Any, Any]]
    __data_keys_fields__: Dict[str, Field[Any, Any]]

    __slots__ = (
        '_field_values',
        '_context',
    )

    def __init__(self, data: Mapping[str, Any]) -> None:
        token = current_schema.set(self)
        try:
            self._field_values: Dict[str, Any] = {}
            self._context = SchemaContext(self)
            self._prepare_from_data(data)
        finally:
            current_schema.reset(token)

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, '__fields__'):
            cls.__fields__ = {}
            cls.__data_keys_fields__ = {}

        members = vars(cls)
        for name, member in members.items():
            if isinstance(member, Field):
                member._bind(name, cls)
                cls.__fields__[name] = member
                cls.__data_keys_fields__[member.load_key] = member
            elif callable(member) and hasattr(member, '__validator_field__'):
                field = member.__validator_field__
                if isinstance(field, str):
                    try:
                        field = members[field]
                    except KeyError:  # pragma: no cover
                        pass
                if not isinstance(field, Field):
                    raise TypeError(f'Validator {member.__name__} got an unknown field {field}')  # pragma: no cover

                field.add_validator(member)

    def _prepare_from_data(self, data: Mapping[str, Any]) -> None:
        fields = self.__data_keys_fields__.copy()
        validators: List[Tuple[Field[Any, Any], Any, LoadContext, bool]] = []
        errors: List[FieldError] = []

        for key, value in data.items():
            try:
                field = fields.pop(key)
            except KeyError:
                token = current_field_name.set(key)
                errors.append(FieldError(f'Invalid or unknown field.'))
            else:
                # See comment in _process_field_values() for explanation on how
                # validators are handled.
                token = current_field_name.set(field._name)
                process_errors = self._process_field_value(field, value, validators)
                errors.extend(process_errors)

            current_field_name.reset(token)

        for _, field in fields.items():
            name = field._name
            token = current_field_name.set(name)
            try:
                if field.required:
                    errors.append(FieldError('This field is required.'))
                if field._default is not MISSING:
                    self._field_values[name] = field._default(self._context, field) if callable(field._default) else field._default
            finally:
                current_field_name.reset(token)

        for field, value, context, raw in validators:
            ctx_token = current_context.set(context)
            field_token = current_field_name.set(field._name)
            schema_token = current_schema.set(self)
            try:
                errors.extend(field._run_validators(value, context, raw=raw))
            finally:
                current_context.reset(ctx_token)
                current_field_name.reset(field_token)
                current_schema.reset(schema_token)

        if errors:
            raise ValidationError(errors)

        self._context._initialized = True

    def _process_field_value(
            self,
            field: Field[Any, Any],
            value: Any,
            validators: Optional[List[Tuple[Field[Any, Any], Any, LoadContext, bool]]] = None,
        ) -> List[FieldError]:

        # A little overview of how external validations are handled by
        # this method:
        #
        # If the validators parameter is not provided (None), the validators
        # are ran directly and any errors raised by them are appended to the
        # list of returned errors. (e.g. Field.__set__ does this)
        #
        # In contrary case, if the validators parameter is provided, it is a
        # list of 4 element tuples: the field to validate, the value validated,
        # the load context, and a boolean indicating whether the validation is
        # performed by raw validators. This validation data appended to the given
        # validators list by this method and the validators are ran lazily later
        # using this data. This is done when validators are ran on initialization
        # of schema. (e.g. Schema._prepare_from_data does this)

        name = field._name
        lazy_validation = validators is not None
        errors: List[FieldError] = []
        validator_errors: List[FieldError] = []
        context = LoadContext(field=field, value=value, schema=self)
        token = current_context.set(context)

        if field._raw_validators and lazy_validation:
            validators.append((field, value, context, True))

        if value is None:
            if field.none:
                self._field_values[name] = None
            else:
                errors.append(FieldError('This field cannot take a None value.'))
            return errors

        if not lazy_validation:
            validator_errors.extend(field._run_validators(value, context, raw=True))
        try:
            final_value = field.value_load(value, context)
        except (ValueError, AssertionError, FieldError) as err:
            if not isinstance(err, FieldError):
                err = FieldError._from_standard_error(err)
            errors.append(err)
        else:
            if not lazy_validation:
                validator_errors.extend(field._run_validators(final_value, context, raw=False))
            else:
                validators.append((field, final_value, context, False))
            if not validator_errors:
                self._field_values[name] = final_value
            errors.extend(validator_errors)
        finally:
            current_context.reset(token)

        return errors

    @property
    def context(self) -> SchemaContext:
        """The context for this schema.

        Schema context holds the information about schema and its state.

        Returns
        -------
        :class:`SchemaContext`
        """
        return self._context

    def get_value_for(self, field_name: str, default: Any = MISSING, /) -> Any:
        """Returns the value for a field.

        If field has no value set, a :class:`ValueError` is raised
        unless a ``default`` is provided.

        Parameters
        ----------
        field_name: :class:`str`
            The name of field to get value for.
        default:
            The default value to return if field has no value.

        Returns
        -------
        The field value.

        Raises
        ------
        RuntimeError
            Invalid field name.
        ValueError
            Field value not set.
        """
        if field_name not in self.__fields__:
            raise RuntimeError(f'Field name {field_name!r} is invalid.')
        try:
            return self._field_values[field_name]
        except KeyError:
            if default is not MISSING:
                return default
            raise ValueError('No value set for this field.') from None

    def dump(self, *, include: Optional[Sequence[str]] = None, exclude: Optional[Sequence[str]] = None) -> Dict[str, Any]:
        """Deserializes the schema.

        The returned value is deserialized data in dictionary form. The
        ``include`` and ``exclude`` parameters are mutually exclusive.

        Parameters
        ----------
        include: Optional[Sequence[:class:`str`]]
            The fields to include in the returned data.
        exclude: Optional[Sequence[:class:`str`]]
            The fields to exclude from the returned data.

        Returns
        -------
        Dict[:class:`str`, Any]
            The deserialized data.

        Raises
        ------
        TypeError
            Both include and exclude provided.
        ValidationError
            Validation failed while deserializing one or more fields.
        """
        fields = set(self.__fields__.keys())
        if include is not None and exclude is not None:
            raise TypeError('include and exclude are mutually exclusive parameters.')
        if include is not None:
            fields = fields.intersection(set(include))
        if exclude is not None:
            fields = fields.difference(set(exclude))

        current_schema.set(self)
        out: Dict[str, Any] = {}
        errors: List[FieldError] = []

        for name in fields:
            field = self.__fields__[name]
            try:
                value = self._field_values[name]
            except KeyError:  # pragma: no cover
                # This should never happen I guess.
                # XXX: Raise an error here?
                continue

            context = DumpContext(
                schema=self,
                field=field,
                value=value,
                included_fields=fields,
            )
            field_token = current_field_name.set(name)
            context_token = current_context.set(context)
            try:
                out[field.dump_key] = field.value_dump(value, context)
            except (ValueError, AssertionError, FieldError) as err:
                if not isinstance(err, FieldError):
                    err = FieldError._from_standard_error(err)
                errors.append(err)
            finally:
                current_field_name.reset(field_token)
                current_context.reset(context_token)

        if errors:
            raise ValidationError(errors)

        return out
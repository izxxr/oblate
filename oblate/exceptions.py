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

from typing import List, Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from oblate.fields import Field

__all__ = (
    'OblateException',
    'ValidationError',
    'SchemaValidationFailed',
)


class OblateException(Exception):
    """The base class for all exceptions provided by the library."""


class ValidationError(OblateException):
    """An error raised when validation fails for a specific field.

    Parameters
    ----------
    message: :class:`str`
        The error message.
    """
    def __init__(self, message: str) -> None:
        self._field: Optional[Field] = None
        self._message = message
        super().__init__(message)

    def _bind(self, field: Field) -> None:
        self._field = field


class SchemaValidationFailed(OblateException):
    """An error raised when a schema fails to initialize due to validation errors.

    This is raised by the library and should not be manually raised by the user.
    """
    def __init__(self, errors: List[ValidationError]) -> None:
        self._errors = errors
        super().__init__('Validation failed for this schema:\n' + self._format())

    def _format(self) -> str:
        raw = self.raw()
        builder = []
        builder.extend('Error: \n'.join(raw['errors']))

        for field, errors in raw['field_errors'].items():
            builder.append(f'In field {field}:')
            for error in errors:
                builder.append(f'  - {error}')

        return '\n'.join(builder)

    def raw(self) -> Dict[str, Any]:
        """Converts the error to raw format.

        This converts the error into a dictionary having two keys:

        - ``errors``
        - ``field_errors``

        The ``errors`` key has validation error messages that are not related
        to a specific field. ``field_errors`` is a dictionary with key being
        the field to which the error belongs and value is the list of error
        messages for that field.
        """
        out = {
            'errors': [],
            'field_errors': {}
        }

        for error in self._errors:
            if error._field is None:
                out['errors'].append(error._message)
            else:
                try:
                    field_errors = out['field_errors'][error._field._name]
                except KeyError:
                    out['field_errors'][error._field._name] = [error._message]
                else:
                    field_errors.append(error._message)

        return out

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

from oblate import fields
import oblate
import pytest

def test_field_object():
    class User(oblate.Schema):
        id = fields.Integer()
        name = fields.String()

    class Game(oblate.Schema):
        id = fields.Integer()
        author = fields.Object(User)

    user_data = {'id': 1, 'name': 'John'}
    game_data = {'id': 2, 'author': user_data}

    game = Game(game_data)
    assert game.author.id == 1
    assert game.author.name == 'John'
    assert game.dump() == game_data

    user_data.pop('id')

    try:
        Game(game_data)
    except oblate.ValidationError as err:
        raw = err.raw()
        assert 'id' in raw['author'][0]
        assert 'required' in raw['author'][0]['id'][0]

    game_data['author'] = 'invalid'  # type: ignore

    with pytest.raises(oblate.ValidationError, match='User object'):
        Game(game_data)

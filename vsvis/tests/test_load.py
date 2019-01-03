# -*- coding: utf-8 -*-
"""
@author: Vladimir Shteyn
@email: vladimir.shteyn@googlemail.com

Copyright Vladimir Shteyn, 2018

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import pytest
import pytestqt
from os.path import join

from ..main_window import VMainWindow
from ..config import TEST_DIR, DataType


folder = join(TEST_DIR, 'data')
filename = join(folder, 'test.h5')

@pytest.fixture
def main_window(qtbot):
    with VMainWindow() as widget:
        widget.show()
        qtbot.add_widget(widget)
        yield widget, qtbot


class TestLoadImage(object):
    """
    Tests for loading image data.
    """
    def test_load(self, main_window):
        widget, qtbot = main_window
        widget.load(filename, DataType.IMAGE, [['/image/data']])


class TestLoadData(object):
    """
    Tests for loading coordinate/marker data.
    """
    def test_load(self, main_window):
        widget, qtbot = main_window
        widget.load(filename, DataType.GROUND_TRUTH,
                    [['/ground_truth/0'],
                     ['/ground_truth/1'],
                     ['/ground_truth/2']])

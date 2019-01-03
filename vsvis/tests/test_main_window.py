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
import pytestqt
import pytest
import h5py
from os.path import abspath, dirname, join
from qtpy.QtCore import Qt, QPoint
from qtpy.QtTest import QTest
from qtpy.QtWidgets import QAction

from ..main_window import VMainWindow
from ..config import TEST_DIR


class TestMainWindowCreate(object):
    """
    The most basic test for whether we can instantiate/show the GUI's main
    window.
    """
    def test_create(self, qtbot):
        with VMainWindow() as widget:
            widget.show()
            qtbot.add_widget(widget)


@pytest.fixture()
def menu_test_fixture(qtbot):
    """
    A fixture for testing the main window's menubar, whose items open file
    dialogs e.g. to open a file or save the current workspace. In order to
    keep our (unit) tests relatively separate from widget to widget, we
    disconnect the widget's signals that are emitted upon a file selection
    being accepted. That is, we're faking existing files with pytest's 'tmpdir'
    fixture, and we don't pass them along for their contents to be parsed and
    inspected by the user in VFileInspectionDialog.
    """
    with VMainWindow() as widget:
        widget.show()
        # widget.filename_accepted[str].disconnect()
        qtbot.add_widget(widget)
        qtbot.add_widget(widget._file_dialog)
        yield widget, widget._file_dialog, qtbot


class TestMenu(object):
    """
    Tests whether the menu buttons work, e.g. whether clicking "Open Image..."
    actually opens a QFileDialog and records the correct filename. As stated
    in the menu_test_fixture docstring, this does not test for file parsing and
    loading functionality. That's tested in the test_file_info_dialog module.
    """
    folder = join(TEST_DIR, 'data')
    tiffilename = join(folder, 'test.tif')
    h5filename = join(folder, 'test.h5')

    def test_clicks(self, menu_test_fixture):
        widget, dialog, qtbot = menu_test_fixture
        qtbot.mouseClick(widget.menu_file, Qt.LeftButton, pos=QPoint(0, 0))


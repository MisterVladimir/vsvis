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

from pytestqt import qt_compat
from pytestqt.qt_compat import qt_api


# copied from pytest-qt package
# functions as a positive control for tests actually running
def test_basics(qtbot):
    """
    Basic test that works more like a sanity check to ensure we are setting up
    a QApplication properly and are able to display a simple event_recorder.
    """
    assert qt_api.QApplication.instance() is not None
    widget = qt_api.QWidget()
    qtbot.addWidget(widget)
    widget.setWindowTitle("W1")
    widget.show()

    assert widget.isVisible()
    assert widget.windowTitle() == "W1"

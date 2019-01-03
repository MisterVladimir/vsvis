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
import os
import sys
import re
from qtpy import QtWidgets

from vsvis.main_window import VMainWindow
from vsvis.file_inspection_dialog import (
    FileLoadingParameter, VFileInspectionDialog, make_dialog)
from vsvis.config import TEST_DIR


def example_app():
    app = QtWidgets.QApplication(sys.argv)
    with VMainWindow() as mw:
        mw.show()
        sys.exit(app.exec_())


def example_file_info_dialog():
    from vsvis import TEST_DIR

    filename = os.path.abspath(os.path.join(
        TEST_DIR, 'data', 'test_file_info_dialog.h5'))
    # print(filename)
    app = QtWidgets.QApplication(sys.argv)
    columns = ['name', 'directory']
    predicted_titles = OrderedDict(
        [('Title 1', columns),
         ('Title 2', columns)])
    dialog = make_dialog(filename, )

    dialog.load(filename, *parameters)
    dialog.add_list_widget('title', ['name', 'directory'])
    dialog.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    print(TEST_DIR)
    example_app()
    # example_file_info_dialog()

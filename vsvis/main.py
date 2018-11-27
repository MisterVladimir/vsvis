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

from vsvis.main_window import make_main_window, DataInspectorWidget
from vsvis.file_inspection_dialog import (FileLoadingParameter,
                                          FileInspectionDialog)
from vsvis import TEST_DIR


def example_app():
    app = QtWidgets.QApplication(sys.argv)
    main_window = make_main_window(DataInspectorWidget)
    main_window.show()
    sys.exit(app.exec_())


def example_file_info_dialog():
    from vsvis.file_inspection_dialog import (
        FileInspectionDialog, FileLoadingParameter)
    from vsvis import TEST_DIR

    filename = os.path.abspath(os.path.join(
        TEST_DIR, 'data', 'test_file_info_dialog.h5'))
    # print(filename)
    app = QtWidgets.QApplication(sys.argv)
    dialog = FileInspectionDialog()

    def get_name(dset):
        regexp = re.compile(r'[a-zA-Z]+')
        name = getattr(dset, 'name')
        name = name.split('/')[-1]
        print(name)
        if regexp.search(name):
            return name
        else:
            return '{:0>5}'.format(name)

    parameters = [
        FileLoadingParameter(
            attr='name',
            column='Name',
            function=get_name),
        FileLoadingParameter(
            attr='directory',
            column='Path',
            function=lambda dset: getattr(dset, 'name')),
        FileLoadingParameter(
            attr='shape', column='Shape'),
        FileLoadingParameter(
            attr='dtype',
            column="Type",
            function=lambda dset: str(getattr(dset, 'dtype')))]

    dialog.load_file(filename, *parameters)
    dialog.add_list_widget('title', ['name', 'directory'])
    dialog.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    example_app()
    # example_file_info_dialog()

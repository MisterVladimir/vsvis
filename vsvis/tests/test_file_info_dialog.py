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
import pandas as pd
from qtpy import QtCore
import os
from abc import ABC

from ..file_inspection_dialog import (
    LabeledListWidget, FileInspectionDialog, FileLoadingParameter)
from ..models import ListModel, DroppableListModel
from .. import TEST_DIR


class AbstractTest(ABC):
    WidgetClass = None
    df_columns_only = pd.DataFrame(columns=['name', 'directory'])
    df_full = pd.DataFrame(columns=['name', 'directory'],
                           data=[[1, 2], [4, 5]])

    def create(self, qtbot, *args, **kwargs):
        widget = self.WidgetClass(*args, **kwargs)
        qtbot.add_widget(widget)
        widget.show()
        return widget


class TestListWidget(AbstractTest):
    WidgetClass = LabeledListWidget

    @pytest.mark.dependency
    def test_create_widget(self, qtbot):
        widget = self.create(qtbot, 'test_title')

        assert widget.isVisible()
        assert widget.groupbox.title() == 'test_title'

    @pytest.mark.dependency(depends=['TestListWidget::test_create_widget'])
    def test_set_basic_model(self, qtbot):
        widget = self.create(qtbot, 'test_title')

        empty_model = ListModel()
        widget.setModel(empty_model)

        columns_only_model = ListModel(self.df_columns_only)
        widget.setModel(columns_only_model)

        model = ListModel(self.df_full)
        widget.setModel(model)

    @pytest.mark.dependency(depends=['TestListWidget::test_set_basic_model'])
    def test_set_droppable_model(self, qtbot):
        widget = self.create(qtbot, 'test_title')

        empty_model = DroppableListModel()
        widget.setModel(empty_model)

        columns_only_model = DroppableListModel(self.df_columns_only)
        widget.setModel(columns_only_model)

        model = DroppableListModel(self.df_full)
        widget.setModel(model)


class TestFileInspectionDialog(AbstractTest):
    WidgetClass = FileInspectionDialog
    parameters = [
        FileLoadingParameter(
            attr='name',
            column='Name',
            function=lambda dset: getattr(dset, 'name').split('/')[-1]),
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

    h5file = os.path.join(TEST_DIR, 'data', 'test_file_info_dialog.h5')

    def create_complete_widget(self, qtbot):
        widget = self.create(qtbot)
        widget.load_file(self.h5file, *self.parameters)
        widget.add_list_widget('title_1', widget.attributes[:2])
        widget.add_list_widget('title_2', widget.attributes[:2])
        return widget

    @pytest.mark.dependency
    def test_add_h5file(self, qtbot):
        widget = self.create(qtbot)
        widget.load_file(self.h5file, *self.parameters)

        table_model = widget.data_preview_table_view.model()
        assert table_model.columnCount() == len(self.parameters)

    @pytest.mark.dependency(depends=['TestFileInspectioDialog::test_add_h5file'])
    def test_add_list_widget(self, qtbot):
        widget = self.create_complete_widget(qtbot)

    @pytest.mark.dependency(depends=['TestFileInspectioDialog::test_add_list_widget'])
    def test_table(self, qtbot):
        widget = self.create_complete_widget(qtbot)

        tree_view = widget.file_structure_tree_view
        tree_view.expandAll()
        tree_model = widget.file_structure_tree_view.model()

        list_view = widget.list_widgets['title_1'].list_view

        table_model = widget.data_preview_table_view.model()

        # test whether clicking on an index selects it
        # and whether clicking on a tree item that corresponds to a dataset
        # results in the apperance of items in the table
        grp1_index = tree_model.index(0, 0, QtCore.QModelIndex())
        clickpos = tree_view.visualRect(grp1_index).center()
        qtbot.mouseClick(tree_view.viewport(), QtCore.Qt.LeftButton, pos=clickpos)
        # try clicking on an h5py group, see if something gets selected
        assert len(tree_view.selectedIndexes()) == 1
        assert table_model.rowCount() == 1

        # click on a dataset
        parent = tree_model.index(2, 0, QtCore.QModelIndex())
        index = tree_model.index(0, 0, parent)
        clickpos = tree_view.visualRect(index).center()
        qtbot.mouseClick(tree_view.viewport(), QtCore.Qt.LeftButton, pos=clickpos)
        assert len(tree_view.selectedIndexes()) == 1
        assert table_model.rowCount() == 1

        # open the node in the QTreeView
        parent = tree_model.index(1, 0, QtCore.QModelIndex())
        parent = tree_model.index(1, 0, parent)
        index = tree_model.index(0, 0, parent)
        clickpos = tree_view.visualRect(index).center()
        qtbot.mouseClick(tree_view.viewport(), QtCore.Qt.LeftButton, QtCore.Qt.ControlModifier, clickpos)
        assert len(tree_view.selectedIndexes()) == 2
        assert table_model.rowCount() == 2
        # assert 0

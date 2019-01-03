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
import numpy as np
import re
import sys
import os
import pandas as pd
from os.path import splitext, basename
from qtpy.QtWidgets import QWidget, QDialog
from qtpy.QtCore import QModelIndex, Slot
from typing import (Callable, Dict, Generator, Optional, NamedTuple, Sequence,
                    Tuple, Union, ValuesView)
from anytree import Node
from collections import OrderedDict, namedtuple
from vladutils.decorators import methdispatch as method_dispatch
from vladutils.iteration import isiterable

from .models.tree import DraggableTreeModel
from .models.table import DroppableListModel, DataFrameModel, ListModel
from .utils import load_node_from_hdf5
from .config import DataType, loadUiType, UI_DIR, TEST_DIR, EXTENSIONS


Ui_GroupBoxClass, GroupBoxBaseClass = loadUiType(
    os.path.join(UI_DIR, 'listbox.ui'))
ColumnType = Union[None, int, slice, Sequence[Union[str, int]]]
PandasType = Union[pd.Series, pd.DataFrame]


class LabeledListWidget(GroupBoxBaseClass, Ui_GroupBoxClass):
    """
    A QListWidget inside a QGroupBox, with "Sort", "Delete", "Clear" buttons on
    the bottom to edit the contents of the list.
    """
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super(LabeledListWidget, self).__init__(parent)
        self.setupUi(self)
        self.groupbox.setTitle(title)

    def model(self) -> Union[DroppableListModel, ListModel]:
        return self.list_view.model()

    def setModel(self, model: Union[DroppableListModel, ListModel]) -> None:
        self.list_view.setModel(model)
        self._connect_buttons()

    def _delete(self, indices: Sequence[QModelIndex]) -> bool:
        model = self.model()
        _indices = [ind.row() for ind in indices]
        return model.removeDataFrameRows(_indices)

    def _connect_buttons(self) -> None:
        model = self.model()
        # https://stackoverflow.com/questions/21586643/pyqt-widget-connect-and-disconnect
        for button in (self.sort_button, self.delete_button, self.clear_button):
            while True:
                try:
                    button.clicked.disconnect()
                except TypeError:
                    break

        self.sort_button.clicked.connect(lambda: model.sort(0))
        self.delete_button.clicked.connect(
            lambda: self._delete(self.list_view.selectedIndexes()))
        self.clear_button.clicked.connect(lambda: model.clear())

    @method_dispatch
    def get_data(self, column: ColumnType = None) -> PandasType:
        return self.model().dataFrame()

    @get_data.register(int)
    @get_data.register(slice)
    def _get_data(self, column: Union[int, slice]) -> PandasType:
        dataframe = self.list_view.model().dataFrame()
        return dataframe.iloc[:, column]

    @get_data.register(str)
    def _get_data(self, column: str) -> pd.Series:
        dataframe = self.list_view.model().dataFrame()
        return dataframe[column]

    @get_data.register(list)
    def _get_data(self, columns: Sequence[Union[str, int]]) -> pd.DataFrame:
        dataframe = self.list_view.model().dataFrame()
        # a hack until I figure out a way to dispatch by the type
        # contained within the list
        columns = [dataframe.columns.get_loc(c) if isinstance(c, str) else c
                   for c in columns]
        return dataframe.iloc[:, list(columns)]


class FileLoadingParameter(NamedTuple):
    """
    attr : str
        Name of the h5py.Group or h5py.Dataset attribute

    column : str
        Name of the column in self.data_preview_table_view in which
        this attribute's value will be displayed while the item is
        selected.

    function : Optional[Callable]
        Function that takes the h5py.Group or h5py.Dataset's 'attr' attribute
        as a single argument.
    """
    attr: str
    column: str
    function: Optional[Callable] = None


Ui_DialogClass, DialogBaseClass = loadUiType(
    os.path.join(UI_DIR, 'file_inspection_dialog.ui'))


class VFileInspectionDialog(DialogBaseClass, Ui_DialogClass):
    """
    dtype : DataType
        DataType of the data being loaded.

    parent : Optional[QWidget]
    """
    def __init__(self, dtype: DataType, parent: Optional[QWidget] = None):
        super(VFileInspectionDialog, self).__init__(parent)
        self.setupUi(self)
        self.dtype = dtype
        self.list_widgets: Dict[str, LabeledListWidget] = dict()
        self.filename: Optional[str] = None
        # columns in the QTableView, which previous attributes of HDF5 Datasets
        self.columns: Sequence[str] = []
        self.attributes: Sequence[str] = []
    #     self._model_setup()

    # def _model_setup(self):
    #     # setup empty model for the tree view
    #     root = Node('root')
    #     model = DraggableTreeModel(root, [])
    #     self.file_structure_tree_view.setModel(model)

    def load(self, filename: str, *parameters: FileLoadingParameter):
        """
        filename : str
            Name of HDF5 file to be inspected.

        parameters : NamedTuple
        """
        if splitext(filename)[1] not in EXTENSIONS[DataType.HD5][0]:
            raise TypeError("{} is not an HDF5 file.".format(basename(filename)))
        self.filename = filename
        self.attributes, self.columns, functions = zip(*parameters)

        # same as
        # args = [attr for attr, _, func in zip(
        #   self.attributes, self.columns, functions) if func is None]
        functions_iter = iter(functions)
        args = tuple(filter(lambda x: not next(functions_iter),
                            self.attributes))

        # same as
        # kwargs = {attr: func for attr, _, func
        #           in zip(self.attributes, self.columns, functions)
        #           if func is not None}
        functions_iter = iter(functions)
        kwargs = dict(filter(lambda x: next(functions_iter),
                             zip(self.attributes, functions)))

        # parse the contents of the HDF5 file and populate the
        # file_structure_tree_view (instance of QTreeView) with the info.
        root = load_node_from_hdf5(filename, *args, **kwargs)
        self.file_structure_tree_view.setModel(
            DraggableTreeModel(root, self.attributes))

        # when a user clicks on items in the QTreeView, their properties -- or
        # at least the properties enumerated in self.columns -- are shown in
        # data_preview_table_view (an instance of QTableView)
        dataframe = pd.DataFrame(columns=self.columns)
        table_model = DataFrameModel(dataframe)
        self.data_preview_table_view.setModel(table_model)

        # after new data loaded, disconnect previous selection models
        selection_model = self.file_structure_tree_view.selectionModel()
        try:
            selection_model.selectionChanged.disconnect(
                self.file_selection_changed)
        except TypeError:
            pass
        selection_model.selectionChanged.connect(self.file_selection_changed)

    def add_list_widget(
            self, title: str, columns: Sequence[str]) -> bool:
        """
        Add a DroppableListWidget which can accept items dragged and dropped
        from the file_structure_tree_view.
        """

        # columns = np.array(columns)
        if not np.all(np.isin(columns, self.attributes)):
            print('{} not a subset of {}'.format(columns, self.attributes))
            return False

        widget = LabeledListWidget(title, self.data_preview_groupbox)
        self.list_layout.addWidget(widget)
        dataframe = pd.DataFrame(columns=columns)
        model = DroppableListModel(dataframe)
        widget.setModel(model)

        self.list_layout.addWidget(widget)
        self.list_widgets[title] = widget

        return True

    @Slot()
    def file_selection_changed(self):
        """
        Every time the TreeView's selection is changed, update the TableModel
        to reflect the current selection. This method isn't the most
        computationally efficient implementation but it's certainly the
        simplest.
        """
        table_model = self.data_preview_table_view.model()
        tree_model = self.file_structure_tree_view.model()
        indices = self.file_structure_tree_view.selectedIndexes()
        as_dict = tree_model.get_nodes_as_dict(
            indices, dict(zip(self.attributes, self.columns)))
        dataframe = pd.DataFrame.from_dict(as_dict)

        dif = len(indices) - table_model.rowCount()
        if dif < 0:
            table_model.removeDataFrameRows(np.arange(abs(dif)))
        elif dif > 0:
            table_model.addDataFrameRows(dif)

        table_model._dataFrame.iloc[:, :] = dataframe
        table_model.layoutChanged.emit()
        return True

    def get_data(self, column: Optional[Union[str, Sequence[str]]] = None,
                 titles: Optional[Union[str, Sequence[str]]] = None
                 ) -> np.ndarray:
        """
        Concatenate and return the data in all ListWidgets.
        """
        widgets: Union[ValuesView[LabeledListWidget],
                       Generator[LabeledListWidget, None, None],
                       Tuple[LabeledListWidget]]
        if titles is None:
            widgets = self.list_widgets.values()
        elif isiterable(titles):
            widgets = (self.list_widgets[t] for t in titles)
        elif isinstance(titles, str):
            widgets = (self.list_widgets[titles], )

        df = pd.concat([w.get_data(column) for w in widgets], axis=1)
        return df.values


def _make_dialog_base(filename, dtype):
    dialog = VFileInspectionDialog(dtype)

    def get_name(dset):
        """
        If a dataset's name consists of numbers only, pad the number with
        zeros. Otherwise, return the name unmodified.
        """
        regexp = re.compile(r'[a-zA-Z]+')
        name = getattr(dset, 'name')
        name = name.split('/')[-1]
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

    dialog.load(filename, *parameters)
    return dialog


def make_dialog(filename: str, names: Dict, dtype: DataType) -> QDialog:
    dialog = _make_dialog_base(filename, dtype)
    for k, v in names.items():
        dialog.add_list_widget(k, v)
    return dialog

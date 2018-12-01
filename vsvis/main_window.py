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
import h5py
import numpy as np
from pandas import concat
from os.path import extsep, join, splitext
from qtpy import QtCore, QtWidgets, uic
from collections import OrderedDict
from typing import Sequence
from vladutils.data_structures import EnumDict

from .file_inspection_dialog import make_dialog
from . import UI_DIR
from .datasource import HDF5Request, HDF5DataSource
from .models.scene import (VScene, MarkerFactory,
                           HDF5ImageManager, TiffImageManager)
from .models.table import HDF5TableModel
from .enums import DataType


class VTabWidget(QtWidgets.QTabWidget):
    def __init__(self, titles: EnumDict, parent=None):
        super().__init__(parent)
        self._widgets = EnumDict([(k, None) for k in titles])
        self.tables = EnumDict([(k, None) for k in titles])
        for k, v in titles:
            self._add_tab(k, v)

    def _add_tab(self, dtype: DataType, name: str):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        table = QtWidgets.QTableView(widget)
        table.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                            QtWidgets.QSizePolicy.Expanding)
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.horizontalHeader().setCascadingSectionResizes(True)
        layout.addWidget(table)
        self.addTab(self.ground_truth_tab, name)

        self.tables[dtype] = table
        self._widgets[dtype] = widget

    def __getitem__(self, key):
        return self.tables[key]

    def __len__(self):
        return len(self.tables)

    def __iter__(self):
        return iter(self.tables)

    def keys(self):
        return self.tables.keys()

    def values(self):
        return self.tables.values()

    def items(self):
        return self.tables.items()

tr = QtCore.QObject.tr
MainWindowClass, MainWindowBaseClass = uic.loadUiType(
    join(UI_DIR, 'main_window2.ui'))


class VMainWindow(MainWindowClass, MainWindowBaseClass):
    file_extensions = EnumDict(
        [(DataType.TIFF_IMAGE, ['tif', 'tiff', 'ome.tif']),
         (DataType.HD5, ['h5', 'hdf5', 'hf5', 'hd5'])])

    list_widget_columns = ['name', 'directory']
    ground_truth_titles = OrderedDict(
        [('Ground Truth Coordinates', list_widget_columns)])
    predicted_titles = OrderedDict(
        [('Probabilities', list_widget_columns),
         ('Predicted Coordinates', list_widget_columns)])
    image_titles = OrderedDict(
        [('Images', list_widget_columns)])
    list_widget_args = EnumDict([
        (DataType.GROUND_TRUTH, ground_truth_titles),
        (DataType.PREDICTED, predicted_titles),
        (DataType.HDF_IMAGE, image_titles)])

    table_columns = EnumDict([
        (DataType.GROUND_TRUTH, ['X', 'Y']),
        (DataType.PREDICTED, ['X', 'Y', 'Probability'])])

    #                             str, DataFrame, DataType
    data_selected = QtCore.Signal(str, object, object)
    predicted_data_selected = QtCore.Signal(dict)
    ground_truth_data_selected = QtCore.Signal(dict)
    image_data_selected = QtCore.Signal([str, list], [str])

    def __init__(self, tabwidget):
        super(MainWindowBaseClass, self).__init__()
        self.setupUi(self)
        self._setup_tables(tabwidget)


        self.filenames = EnumDict([
            (DataType.GROUND_TRUTH, None),
            (DataType.PREDICTED, None),
            (DataType.IMAGE, None)])
        self.dataset_names = EnumDict([
            (DataType.GROUND_TRUTH, None),
            (DataType.PREDICTED, None),
            (DataType.HDF_IMAGE, None)])

        self._signals_setup()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        for item in (self._image_datasource, self._ground_truth_data, self._predicted_data):
            try:
                item.close()
            except AttributeError:
                pass

    def _setup_tables(self, tabwidget):
        tabwidget.setParent(self.tables_parent_widget)
        self.tables_parent_widget.layout().addWidget(tabwidget)
        self.tables_tab_widget = tabwidget

    def _set_scene_common(self, manager):
        groups = OrderedDict([
            ('ground_truth', MarkerFactory(color=QtCore.Qt.green)),
            ('predicted', MarkerFactory(color=QtCore.Qt.red))])
        scene = VScene(manager, groups)
        self.graphics_view.setScene(scene)

    @QtCore.Slot(str, list)
    def set_scene(self, filename: str, handles: Sequence[str]) -> None:
        try:
            self._image_datasource.close()
        except AttributeError:
            pass
        request = HDF5Request(filename, 0, *handles)
        datasource = HDF5DataSource(filename, request)
        self._image_datasource = datasource

        image_manager = HDF5ImageManager(datasource)
        self._set_scene_common(image_manager)

    # @QtCore.Slot(str)
    # def set_scene(self, filename: str) -> None:
    #     datasource = TiffDatasource(filename)
    #     try:
    #         self._image_datasource.close()
    #     except AttributeError:
    #         pass
    #     self._image_datasource = datasource

    #     image_manager = TiffImageManager(datasource)
    #     self._set_scene_common(image_manager)

    def _signals_setup(self) -> None:
        self.action_open_ground_truth.triggered.connect(
            lambda: self.open(DataType.GROUND_TRUTH))
        self.action_open_predicted.triggered.connect(
            lambda: self.open(DataType.PREDICTED))
        self.action_open_image.triggered.connect(
            lambda: self.open(DataType.IMAGE))

        self.image_data_selected[str, list].connect(self.set_scene)
        # self.image_data_selected[str].connect(self.set_scene)

        self.predicted_data_selected[dict].connect()
        self.ground_truth_data_selected[dict].connect()

        self.graphics_view_scrollbar.valueChanged[int].connect(
            lambda index: self.scrollbar_index_changed(index))

    def _file_open_dialog(self, **extensions):
        ext = [[''] + list(ext) for ext in extensions.values()]
        keys = extensions.keys()
        extlist = [tr(self, k) + "(" + ' *.'.join(e) + ")" for k, e in zip(keys, ext)]
        extstring = ';;'.join(extlist)
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, tr(self, 'Open File'), '', extstring, None,
            QtWidgets.QFileDialog.DontUseNativeDialog)

        return filename

    def _hdf5_file_open_dialog(self):
        key = 'HDF5 Files'
        extensions = {key: self.extensions[key]}
        return self._file_open_dialog(**extensions)

    def _open_hdf5_file_inspection_widget(
            self, filename: str, *list_titles: str):
        names = OrderedDict(
            [(title, ['name', 'directory']) for title in list_titles])
        return make_dialog(filename, names)

    def load_data(self, filename, data, flag):
        pass

    def _open_inspection_widget(self, filename: str, flag: DataType):
        def get_dialog_data(widget):
            titles = self.list_widget_args[flag].keys()
            df = [widget.list_widgets[t].get_data('directory') for t in titles]
            return concat(df, axis=1)

        dialog = make_dialog(filename, self.list_widget_args[flag], flag)
        dialog.button_box.accepted.connect(
            lambda: self.load_data(filename, get_dialog_data(dialog), flag))
        dialog.show()

    def open(self, flag: DataType) -> None:
        enum_to_name = EnumDict([
            (DataType.HD5, 'HDF5 Files'),
            (DataType.TIFF_IMAGE, 'Tiff Files')])
        extensions = dict(zip(enum_to_name[flag], self.extensions[flag]))
        filename = self._file_open_dialog(**extensions)[0]
        file_ext = splitext(filename).split(extsep)[1]
        if file_ext in self.extensions[DataType.TIFF_IMAGE]:
            raise NotImplementedError('Loading Tiff images is not yet '
                                      'implemented. Please use HDF5 data.')
        else:
            self._open_inspection_widget(filename, flag)
        # QtWidgets.QFileDialog.getOpenFileName(
        #     self, tr(self, 'Open File'), '',
        #     tr(self, 'HDF5 Files (*.h5 *.hdf5 *.hf5 *.hd5)'),
        #     None, QtWidgets.QFileDialog.DontUseNativeDialog)


    @QtCore.Slot()
    def open_image(self) -> None:
        filename = self._file_open_dialog(**self.extensions)
        if splitext(filename)[1][1:] in self.extensions['HDF5 Files']:
            dialog = self._open_hdf5_file_inspection_widget(filename, 'Image')
            dialog.button_box.accepted.connect(
                self.image_data_selected.emit(filename, dialog.list_widgets['Image'].get_data('directory')))
        else:
            self.image_data_selected.emit(filename)

    @QtCore.Slot()
    def open_ground_truth(self) -> None:
        filename = self._hdf5_file_open_dialog()
        dialog = self._open_hdf5_file_inspection_widget(
            filename, 'Ground Truth Coordinates')
        dialog.button_box.accepted.connect(self.ground_truth_data_selected.emit(
                {name: widget.get_data('directory') for name, widget in dialog.list_widgets.items()}))

    @QtCore.Slot()
    def open_predicted(self) -> None:
        filename = self._hdf5_file_open_dialog()
        dialog = self._open_hdf5_file_inspection_widget(
            filename, 'Predicted Coordinates', 'Probabilities')
        dialog.button_box.accepted.connect(self.predicted_data_selected.emit(
                {name: widget.get_data('directory') for name, widget in dialog.list_widgets.items()}))

    @QtCore.Slot()
    def save(self):
        pass

    @QtCore.Slot()
    def save_as(self):
        pass

    @QtCore.Slot()
    def quit(self):
        pass

    def _set_image(self, index):
        scene = self.graphics_view.scene()
        im = scene.image_manager.request(index)
        pixmap = scene.array2pixmap(im)
        scene.set_pixmap(pixmap)

    def _set_ground_truth_data(self, info: dict):
        self._ground_truth_data = h5py.File()
        for k, v in info.items():
            self._ground_truth_coordinate_keys = 
            

    def _set_ground_truth_table_model(self, index):
        coordinate_key = self._ground_truth_coordinate_keys[index]
        coordinates = self._ground_truth_data[coordinate_key].value

        model = HDF5TableModel([coordinates], ['x', 'y'])
        self.ground_truth_table_view.setModel(model)

        scene = self.graphics_view.scene()
        scene.add_markers('ground_truth', coordinates)

    def _set_predicted_table_model(self, index):
        coordinate_key = self._predicted_coordinate_keys[index]
        coordinates = self._predicted_data[coordinate_key].value
        probability_key = self._predicted_probability_keys[index]
        probabilities = self._predicted_data[probability_key].value

        model = HDF5TableModel([coordinates, probabilities], ['x', 'y', 'p'])
        self.ground_truth_table_view.setModel(model)

        scene = self.graphics_view.scene()
        scene.add_markers('predicted', coordinates, probability=probabilities)

    @QtCore.Slot(int)
    def scrollbar_index_changed(self, index: int):
        self._set_image(index)
        self._set_ground_truth_table_model(index)
        self._set_predicted_data(index)


def make_main_window(central_widget_class, *args, **kwargs):
    window = VMainWindow(central_widget_class)
    scene = VScene(['ground_truth', 'predicted'])
    window.central_widget.graphics_view.setScene(scene)
    return window

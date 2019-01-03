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
from qtpy import QtCore, QtWidgets

from qtpy.QtCore import QObject, Qt, Property, Signal, Slot


from typing import Any, Dict, Iterable, MutableSet, Optional, Sequence, Tuple
from functools import partialmethod
from collections import OrderedDict
from vladutils.data_structures import EnumDict
from vladutils.iteration import isiterable

from .models.table import HDF5TableModel
from .models.scene import VGraphicsScene
from .models.marker import MarkerFactory
from .datasource import HDF5DataSource
from .config import DataType, MarkerVisible, DATAPARAM, DATATYPES, NAMES
from .widgets import VTabWidget, VWarningMessageBox
from .utils import gui_error


def requires(dtype: DataType):
    def wrapper(func):
        def wrapped(self, *args, **kwargs):
            if not any(self.datasources[dtype]):
                return None
            else:
                return func(self, *args, **kwargs)
        return wrapped
    return wrapper


class Controller(QObject):
    """
    Coördinates the display of markers and images.

    Parameters
    ------------
    scene : QtWidgets.QGraphicsScene
    tabwidget : widgets.VTabWidget
    columns : EnumDict
    datasources : EnumDict
    """
    datasource_about_to_load = Signal(object)
    datasource_loaded = Signal(object)
    index_about_to_change = Signal()
    index_changed = Signal(int)

    _data_loaded = Signal(object)
    _image_loaded = Signal()

    def __init__(self, scene: VGraphicsScene, tabwidget: VTabWidget, groupbox):
        super().__init__()
        self._warning_dialog = VWarningMessageBox()
        self.scene = scene
        self.tabwidget = tabwidget
        self.groupbox = groupbox

        # dtypes = DATATYPES + [DataType.IMAGE]
        self._visible_marker_dtypes = 0
        self._marker_group_indices = dict()
        self._markers_to_hide = dict()
        self._markers_to_show = dict()
        self.datasources = dict()

        self.current_index = 0
        self._signals_setup()

    def cleanup(self):
        for source in self.datasources.values():
            source.cleanup()

    def _signals_setup(self):
        # signals from the coordinate tables to Markers in GraphicsView:
        # setting them, making them visible/invisible
        self.tabwidget.tab_added[object].connect(
            lambda dtype: self._connect_tables(dtype, True))
        self.tabwidget.model_about_to_be_reset[object].connect(
            lambda dtype: self._connect_tables(dtype, False))
        self.tabwidget.model_reset[object].connect(
            lambda dtype: self._connect_tables(dtype, True))

        self.datasource_about_to_load[object].connect(
            self.tabwidget.clear_selection)

        self.datasource_loaded[object].connect(self._update_table_model)
        self.datasource_loaded[object].connect(self._marker_reset_dispatch)

        # signals from the GroupBox where marker visual
        # parametrs (e.g. color, shape, etc.) are set
        self.groupbox.check_state_changed[int, object].connect(
            self.toggle_by_dtype)
        self.groupbox.marker_size_changed[int, object].connect(
            self._set_marker_size)
        self.groupbox.marker_color_changed['QColor', object].connect(
            self._set_marker_color)
        self.groupbox.marker_shape_changed[object, object].connect(
            self._set_marker_shape)
        self.groupbox.marker_fill_changed[bool, object].connect(
            self._set_marker_fill)

    @Slot(object, bool)
    def _connect_tables(self, dtype: DataType, connect: bool):
        """
        Connects or disconnects tables' "selection_changed" signal to the
        method controlling Marker visibility/invisibility in the GraphicsView.
        """
        print('connecting: {}, {}'.format(repr(dtype), connect))
        keys = (k for k in self.tabwidget.tables if k & dtype)
        tables = (self.tabwidget.tables[k] for k in keys)
        for t in tables:
            signal = t.selection_changed[
                'QItemSelection', 'QItemSelection', object]
            if connect:
                method = getattr(signal, 'connect')
            else:
                method = getattr(signal, 'disconnect')
            method(self.toggle_by_selection)

    def _marker_reset_dispatch(self, dtype: DataType):
        if dtype & DataType.IMAGE:
            self._set_image(self.current_index)
        elif dtype & DataType.DATA:
            self._reset_scene_markers(dtype)

    @Slot(object)
    def _reset_scene_markers(self, dtype: DataType):
        """
        Create  for this dtype have not yet been created. 
        """
        print('adding markers of dtype: {}'.format(repr(dtype)))
        if not self.scene.has_markers(dtype):
            self._add_top_level_group(dtype)
            print('added top level group: {}'.format(repr(dtype)))
        if not self.scene.has_markers(dtype, self.current_index):
            key = self.scene.groups[dtype].add_subgroup(self.current_index)
            print('adding index: {}'.format(self.current_index))
            print('key: {}'.format(key))
            self._add_markers(dtype, key)

    def _reset_marker_group(self, dtype: DataType):
        """
        Remove all the Markers and VGraphicsGroups associated with dtype.
        """
        # when a new top level group is added (a tabwidget tab should be added
        # too), register a new Marker dtype whose state we track via the three
        # dictionaries below
        self.scene.delete_top_level_group(dtype)

        self._marker_group_indices[dtype] = set()
        self._markers_to_hide[dtype] = set()
        self._markers_to_show[dtype] = set()

    def _add_top_level_group(self, dtype: DataType):
        print('adding top level group, dtype: {}'.format(repr(dtype)))
        self._reset_marker_group(dtype)
        self.scene.add_top_level_group(dtype)

    def _add_markers(self, dtype: DataType, index: int):
        source = self.datasources[dtype]
        coordinates = source.request(index)
        factory = self.groupbox.create_factory(dtype)
        markers = [factory(x, y) for x, y in coordinates[:, :2]]
        print('adding markers: {}'.format(markers))
        group = self.scene.groups[dtype]
        subgroup = group[index]
        subgroup.replace_child_items(markers, vis=False)

    def _delete_datasource(self, dtype: DataType):
        self.scene.delete_top_level_group(dtype)
        self._marker_group_indices[dtype] = set()
        self._markers_to_hide[dtype] = set()
        self._markers_to_show[dtype] = set()

    def _set_marker_property(self, setter_name, value, dtype):
        for groups in self.scene.groups[dtype]:
            for g in groups:
                setter = getattr(g, setter_name)
                setter(value)

    _set_marker_color = partialmethod(_set_marker_property, 'set_marker_color')
    _set_marker_fill = partialmethod(_set_marker_property, 'set_marker_fill')
    # VGraphicsGroup.set_marker_shape not implemented
    _set_marker_shape = partialmethod(lambda: None)
    # _set_marker_shape = partialmethod(_set_marker_property, 'set_marker_shape')
    _set_marker_size = partialmethod(_set_marker_property, 'set_marker_size')

    def warn(self, message: str) -> bool:
        self._warning_dialog.setInformativeText(message)
        result = self._warning_dialog.exec_()
        if result == VWarningMessageBox.Yes:
            return True
        elif result == VWarningMessageBox.No:
            return False

    def _empty_datasource(self, dtype: DataType):
        if dtype & DataType.IMAGE:
            pass
        elif dtype & DataType.DATA:
            self.tabwidget.clear_model(dtype)
            self.scene.delete_markers(dtype, slice(None))
            for source in self.datasources[dtype]:
                if source is not None:
                    source.cleanup()
                source = None

    def set_datasource(self, datasource: HDF5DataSource, dtype: DataType,
                       name: Optional[str] = None, ind: Optional[int] = None):
        # TODO: add appropriate gui_error wrapper
        if dtype in self.datasources:
            old = self.datasources[dtype]
            for v in old:
                v.cleanup()

        self.datasource_about_to_load.emit(dtype)
        self.datasources[dtype] = datasource
        self.datasource_loaded.emit(dtype)

    def has_data(self, dtype: DataType) -> bool:
        return any(self.datasources[dtype])

    @Slot(object)
    def _update_table_model(self, dtype):
        print('updating table model')
        if dtype & DataType.DATA and dtype not in self.tabwidget.tables:
            print('adding tab: {}'.format(repr(dtype)))
            columns = DATAPARAM[dtype]
            tab_name = NAMES[dtype]
            self.tabwidget.add_tab(dtype, tab_name, columns)
            self.index_about_to_change.connect(
                lambda: self.tabwidget.clear_selection(dtype))
        if dtype & DataType.DATA:
            print('setting model')
            source = self.datasources[dtype]
            data = source.request(self.current_index)
            self.tabwidget.setModel(dtype, data)

    def _update_visible_marker_indices(
            self, selected: Iterable[int], deselected: Iterable[int],
            dtype: DataType) -> Tuple[MutableSet[int]]:
        """
        Updates the indices of markers to be shown and markers to be hidden the
        next time 'dtype' markers are visible.
        """
        hide = self._markers_to_hide[dtype]
        hide.update(deselected)

        show = self._markers_to_show[dtype]
        show.update(selected)

        intersection = set.intersection(show, hide)
        hide.difference_update(intersection)
        show.difference_update(intersection)
        print('updating shown indices:  {}'.format(show))
        print('updating hidden indices: {}'.format(hide))
        return show, hide

    # @requires(DataType.IMAGE)
    @Slot('QItemSelection', 'QItemSelection', object)
    def toggle_by_selection(self, selected, deselected, dtype) -> bool:
        selected = [ind.row() for ind in selected.indexes()]
        deselected = [ind.row() for ind in deselected.indexes()]
        print('toggle by selection: {}'.format(repr(dtype)))
        print('selected:   {}'.format(selected))
        print('deselected: {}'.format(deselected))
        show, hide = self._update_visible_marker_indices(
            selected, deselected, dtype)
        if dtype & self._visible_marker_dtypes:
            # XXX not sure what to do if making a marker invisible fails
            # reset_result = self._reset_scene_markers(dtype)
            print('showing')
            # if reset_result in (True, None):
            shown = self.scene.set_markers_visible(
                dtype, self.current_index, True, show)
            if shown:
                self._markers_to_show[dtype] = set()
                print('showing worked')
            else:
                print('shown failed: {}'.format(hidden))

            hidden = self.scene.set_markers_visible(
                dtype, self.current_index, False, hide)
            if hidden:
                self._markers_to_hide[dtype] = set()
                print('hiding worked')
            else:
                print('hidden failed: {}'.format(hidden))

            # elif isinstance(reset_result, int):
            #     print('reset_result: {}'.format(reset_result))
            # elif reset_result is False:
            #     print('reset_result: {}'.format(reset_result))

            # print('hiding')
            return True
        return False

    # @requires(DataType.IMAGE)
    @Slot(int, object)
    def toggle_by_dtype(self, state, dtype):
        index = self.current_index

        if state == Qt.Unchecked:
            self._visible_marker_dtypes ^= dtype
            markers = self.scene.get_markers(
                dtype, self.current_index, MarkerVisible.true)
            hidden = [m.key for m in markers]
            print('hidden: {}'.format(hidden))
            self.scene.set_markers_visible(dtype, index, False, hidden)
            self._markers_to_show[dtype].update(hidden)

        elif state == Qt.Checked:
            self._visible_marker_dtypes |= dtype
            show, hide = self._update_visible_marker_indices([], [], dtype)
            self.scene.set_markers_visible(dtype, index, True, show)
            self._markers_to_hide[dtype].clear()
            self._markers_to_show[dtype].clear()

    @Slot(int)
    def set_index(self, index: int):
        self.index_about_to_change.emit()
        self.current_index = index
        self._set_table_models(index)
        self._set_image(index)
        # add new markers if necessary
        datakeys = (k for k in self.datasources if k & DataType.DATA)
        for key in datakeys:
            self._reset_scene_markers(key)
        self.index_changed.emit(index)

    # @gui_error('Has image data been loaded?')
    def _set_image(self, index: int):
        source = self.datasources[DataType.IMAGE]
        image = source.request(index).squeeze()
        pixmap = self.scene.array2pixmap(image, rescale=True)
        self.scene.set_pixmap(pixmap, index)

    # def _set_scene_markers(self, index: int):
    #     for dtype, group in self.scene.groups.items():
    #         if self.current_index in group:
    #             # TODO update marker indices
    #             self._marker_group_indices[dtype] = set()
    #         else:
    #             group.add_subgroup(self.current_index)
    #         # XXX should I then set all markers to invisible or visible?
    #         #  this should have been set already though, right?

    # @gui_error('Has ground truth or predicted data been loaded?')
    def _set_table_models(self, index: int):
        print('setting table models')
        print('dtypes: {}'.format(self.tabwidget.dtypes))
        for dtype in self.tabwidget.dtypes:
            print(dtype)
            source = self.datasources[dtype]
            dset = source.request(index)
            print('dset: ')
            print(dset)
            self.tabwidget.setModel(dtype, dset)

    @property
    def current_index(self):
        return self._current_index

    @current_index.setter
    def current_index(self, value):
        self._current_index = value

    @property
    def dtypes(self):
        return list(self.tabwidget.keys())

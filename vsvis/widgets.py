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
import pandas as pd
from qtpy.QtWidgets import (
    QAbstractItemView, QAbstractItemView, QColorDialog, QGraphicsView,
    QGroupBox, QMessageBox, QSizePolicy, QScrollBar, QSlider, QTabWidget,
    QTableView, QVBoxLayout, QWidget)
from qtpy.QtCore import Property, QItemSelectionModel, QObject, QRect, Qt, Signal, Slot
from qtpy.QtGui import QColor, QIcon, QPalette
from qtpy.uic import loadUiType
from functools import partialmethod
from typing import Optional, Union
from vladutils.data_structures import EnumDict
from collections import deque, OrderedDict
from typing import Sequence, List
from os.path import join

from .config import UI_DIR, DATATYPES, DataType, Shape
from .models.table import DataFrameModel
from .models.marker import Marker, MarkerFactory


class VGraphicsView(QGraphicsView):
    """
    Zoomable GraphicsView.
    """
    # minimum image view size
    minimum_size = (256, 256)
    # sensitivity to zoom
    zoom_rate = 1.1

    def wheelEvent(self, event):
        factor = self.zoom_rate**(event.angleDelta().y() / 120.)
        self.scale(factor, factor)

    @Slot()
    def zoom_in(self):
        self.scale(self.zoom_rate, self.zoom_rate)

    @Slot()
    def zoom_out(self):
        self.scale(1. / self.zoom_rate, 1. / self.zoom_rate)

    @Slot()
    def fit_to_window(self):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)


class VAbstractSliderMixin(object):
    """
    A mix-in class for classes derived from QAbstractSlider. Its central
    feature is the value_changed signal, which, unlike QAbstractSlider's
    valueChanged -- is not emitted when the slider is being dragged. Connect to
    value_changed instead of valueChanged if executing a computationally-
    expensive operations when the slider's/scrollbar's index value changes.
    """
    value_changed = Signal(int)

    def __init__(self, *args, **kwargs):
        self._signals_setup()

    def _signals_setup(self):
        # https://stackoverflow.com/questions/16460746/detect-if-the-arrow-button-from-qscrollbar-is-pressed
        self.valueChanged[int].connect(self._emit_value_changed)
        self.sliderReleased.connect(self._emit_value_changed)

    @Slot()
    @Slot(int)
    def _emit_value_changed(self, index: int = None):
        if not self.isSliderDown():
            self.value_changed.emit(self.value())


class VProbabilitySlider(QSlider, VAbstractSliderMixin):
    pass


class VScrollBar(QScrollBar, VAbstractSliderMixin):
    pass


class VTabTableView(QTableView):
    selection_changed = Signal(
        'QItemSelection', 'QItemSelection', object)

    def __init__(
            self, dtype: DataType, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.dtype = dtype

    @Slot('QItemSelection', 'QItemSelection')
    def selectionChanged(self, selected, deselected):
        super().selectionChanged(selected, deselected)
        self.selection_changed.emit(selected, deselected, self.dtype)


class VTabWidget(QTabWidget):
    """
    Parameters
    ------------
    titles : EnumDict
        Keys are a DataType and values are the tab's label for that DataType.
    """
    # _columns = EnumDict([
    #     (DataType.GROUND_TRUTH, ['X', 'Y']),
    #     (DataType.PREDICTED, ['X', 'Y', 'Probability'])])
    tab_added = Signal(object)
    model_reset = Signal(object)
    model_about_to_be_reset = Signal(object)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self._widgets = dict()
        self.tables = dict()
        self._columns = dict()
        self._index_list = deque()
        self._signals_setup()

    def _signals_setup(self):
        pass
        #  self.model_about_to_be_reset[object].connect(self.clear_selection)

    def _get_previous_index(self):
        try:
            return self._index_list[1]
        except IndexError:
            return None

    # @Slot(int)
    # def _set_previous_index(self, value: int):
    #     self._index_list.appendleft(value)
    #     if len(self._index_list) > 2:
    #         self._index_list.pop()

    # def _reset_previous_index(self):
    #     self._index_list = deque()

    # previous_index = Property(
    #     int, _get_previous_index, _set_previous_index, _reset_previous_index)

    @property
    def dtypes(self):
        return [k for k, v in self.tables.items() if v is not None]

    def add_tab(self, dtype: DataType,
                name: str, columns: Sequence[str]) -> bool:

        if dtype in self._widgets:
            raise AttributeError(
                "{} widget has already been set.".format(dtype))

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        table = VTabTableView(dtype, parent=widget)
        table.setSizePolicy(QSizePolicy.Preferred,
                            QSizePolicy.Expanding)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.horizontalHeader().setCascadingSectionResizes(True)
        layout.addWidget(table)
        index = self.addTab(widget, name)

        self.tables[dtype] = table
        self._widgets[dtype] = table
        self._columns[dtype] = columns
        self.tab_added.emit(dtype)
        print('tab added: {}'.format(repr(dtype)))
        return True

    def __getitem__(self, dtype):
        return self.tables[dtype]

    def __setitem__(self, key, value):
        pass

    def __len__(self):
        return len(self.tables)

    def __iter__(self):
        return iter(self.tables)

    def __contains__(self, value):
        return value in self.tables

    def keys(self):
        return self.tables.keys()

    def values(self):
        return self.tables.values()

    def items(self):
        return self.tables.items()

    def setModel(self, dtype: DataType, data: np.ndarray) -> None:
        print('data: ')
        print(data[:3])
        print('')
        self.model_about_to_be_reset.emit(dtype)
        cols = self._columns[dtype]
        df = pd.DataFrame(data, columns=cols)
        model = DataFrameModel(df)
        table = self.tables[dtype]
        table.setModel(model)
        self.model_reset.emit(dtype)

    def clear_model(self, dtype):
        self.model_about_to_be_reset.emit(dtype)
        for table in self.tables[dtype]:
            table.setModel(DataFrameModel())
        self.model_reset.emit(dtype)

    @Slot(object)
    def clear_selection(self, dtype: DataType):
        tables = (self.tables[k] for k in self if k & dtype)
        for t in tables:
            selection_model = t.selectionModel()
            selection_model.clearSelection()

    def setSelectionMode(self, mode: int):
        """
        QAbstractItemView.ExtendedSelection
        QAbstractItemView.NoSelection
        """
        for table in self.values():
            table.setSelectionMode(mode)


class _VMessageBoxBase(QMessageBox):
    vicon = QMessageBox.NoIcon
    vtitle = ''
    vbuttons = QMessageBox.NoButton

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setIcon(self.vicon)
        self.setText(self.vtitle)
        self.setStandardButtons(self.vbuttons)


class VErrorMessageBox(_VMessageBoxBase):
    vicon = QMessageBox.Critical
    vtitle = 'A CRITICAL ERROR HAS OCCURED'
    vbuttons = QMessageBox.Ok

    def get_traceback(self) -> str:
        return self.detailedText()

    def set_traceback(self, text: str):
        self.setDetailedText(text)
        if text:
            self.setDefaultButton(QMessageBox.Ok)
        else:
            self.setDefaultButton(QMessageBox.NoButton)


class VWarningMessageBox(_VMessageBoxBase):
    icon = QMessageBox.Warning
    title = 'WARNING'
    vbuttons = QMessageBox.Yes | QMessageBox.No


Ui_VMarkerOptionsClass, VMarkerOptionsBaseClass = loadUiType(
    join(UI_DIR, 'marker_options_widget.ui'))


class VMarkerOptionsWidget(VMarkerOptionsBaseClass, Ui_VMarkerOptionsClass):
    """
    This widget lets the user select how Markers in the image appear.

    Parameters
    ------------
    checkbox_text : str
        Text placed next to the checkbox.

    dtype : DataType
        The type of data (see: DATATYPES) this widget is responsible for.

    color : Optional[QColor, int]
        The default color of widgets.
    """
    check_state_changed = Signal(int)
    color_changed = Signal(QColor)
    fill_changed = Signal(bool)
    shape_changed = Signal(object)
    size_changed = Signal(float)

    def __init__(self, checkbox_text: str, dtype: DataType,
                 color: Union[QColor, int] = Qt.white,
                 parent: Optional[QWidget] = None):
        super(VMarkerOptionsWidget, self).__init__(parent)
        self.setupUi(self)
        self.checkbox_label.setText(checkbox_text)
        self.dtype = dtype
        self.current_color = color
        self._signals_setup()
        self.setEnabled(False)

    def _signals_setup(self):
        self.select_color_button.clicked.connect(self._select_color)
        self.checkbox.stateChanged[int].connect(self._emit_check_state_changed)
        self.spinbox.valueChanged[int].connect(self._emit_size_changed)
        self.combobox.currentIndexChanged[int].connect(self._emit_shape_changed)

    @Slot(int)
    def _emit_check_state_changed(self, state):
        self.check_state_changed.emit(state)

    @Slot(int)
    def _emit_shape_changed(self, shape):
        self.shape_changed.emit(self.current_shape)

    @Slot(float)
    def _emit_size_changed(self, size):
        self.size_changed.emit(size / 2.)

    @Slot()
    def _select_color(self):
        color = QColorDialog.getColor()
        print('selected color: {}'.format(repr(color)))
        if color.isValid():
            self.current_color = color

    def add_marker_shape(self, shape: Shape, icon: QIcon):
        self.combobox.addItem(icon, '', shape)

    @Property('QColor')
    def current_color(self):
        return self._current_color

    @current_color.setter
    def current_color(self, color: QColor):
        self._current_color = color

        # https://stackoverflow.com/questions/21685414/qt5-setting-background-color-to-qpushbutton-and-qcheckbox
        pal = self.select_color_button.palette()
        pal.setColor(QPalette.Button, color)
        self.select_color_button.setPalette(pal)
        self.select_color_button.update()
        self.color_changed.emit(color)

    @Property(bool)
    def current_fill(self):
        # TODO: implement this
        return True

    @Property(object)
    def current_shape(self):
        return self.combobox.currentData()

    @Property(int)
    def current_size(self):
        return self.spinbox.value()

    @Property(int)
    def check_state(self) -> int:
        return self.checkbox.checkState()

    def create_factory(self) -> MarkerFactory:
        """
        Creates a MarkerFactory based on the current user-defined settings.
        """
        return MarkerFactory(self.current_shape, self.current_color,
                             self.current_size, self.current_fill)


class VMarkerOptionsGroupBox(QGroupBox):
    # second parameter is a DataType
    check_state_changed = Signal(int, object)
    marker_color_changed = Signal(QColor, object)
    marker_fill_changed = Signal(bool, object)
    marker_shape_changed = Signal(object, object)
    marker_size_changed = Signal(float, object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgets = {}

    def colors(self):
        return EnumDict([(w.dtype, w.current_color) for w in self._widgets])

    @Property(list)
    def dtypes(self):
        return [c.dtype for c in self.widgets.values()]

    def add_widget(self, text: str, dtype: DataType,
                   color: Optional[int] = Qt.white,
                   enabled: Optional[bool] = False):
        widget = VMarkerOptionsWidget(text, dtype, color, self)
        layout = self.layout()
        layout.addWidget(widget)
        self.widgets[dtype] = widget

        widget.check_state_changed[int].connect(
            lambda i: self.check_state_changed.emit(i, dtype))
        widget.color_changed['QColor'].connect(
            lambda c: self.marker_color_changed.emit(c, dtype))
        widget.size_changed[float].connect(
            lambda sz: self.marker_size_changed.emit(sz, dtype))
        widget.shape_changed[object].connect(
            lambda sh: self.marker_shape_changed.emit(sh, dtype))
        widget.setEnabled(enabled)

    @Property(list)
    def checked(self) -> List:
        return [child.check_state() for child in self.widgets.values()]

    def create_factory(self, dtype: DataType) -> MarkerFactory:
        if dtype & DataType.DATA:
            widget = self.widgets[dtype]
            return widget.create_factory()

    @Slot(object)
    def enable(self, dtype: DataType,
               enabled: Optional[bool] = True) -> Union[bool, DataType]:
        """
        Enables a VMarkerOptionsWidget in self.widgets.
        """
        if dtype & DataType.DATA:
            widget = self.widgets[dtype]
            widget.setEnabled(enabled)
            return True
        return False

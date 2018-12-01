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
from vladutils.data_structures import EnumDict

from .enums import DataType


class VGraphicsView(QtWidgets.QGraphicsView):
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

    @QtCore.Slot()
    def zoom_in(self):
        self.scale(self.zoom_rate, self.zoom_rate)

    @QtCore.Slot()
    def zoom_out(self):
        self.scale(1. / self.zoom_rate, 1. / self.zoom_rate)

    @QtCore.Slot()
    def fit_to_window(self):
        self.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)


class VProbabilitySlider(QtWidgets.QSlider):
    @QtCore.Slot(int)
    def activate(self, index):
        if index == 0:
            self.setEnabled(False)
        elif index == 1:
            self.setEnabled(True)

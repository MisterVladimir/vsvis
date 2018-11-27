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


class VGraphicsView(QtWidgets.QGraphicsView):
    """
    Zoomable GraphicsView.
    """
    # minimum image view size
    minimum_size = (256, 256)
    # sensitivity to zoom
    zoom_rate = 1.1

    def __init__(self, parent=None):
        super().__init__(parent)

    def wheelEvent(self, event):
        factor = self.zoom_rate**(event.angleDelta().y() / 120.)
        self.scale(factor, factor)
        # event.accept()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Equal:
            self.scale(self.zoom_rate, self.zoom_rate)
        elif event.key() == QtCore.Qt.Key_Minus:
            self.scale(1. / self.zoom_rate, 1 / self.zoom_rate)
        # event.accept()

    def fit_to_window(self):
        self.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)

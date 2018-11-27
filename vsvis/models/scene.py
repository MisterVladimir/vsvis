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
from enum import Flag, auto
from qtpy import QtCore, QtGui, QtWidgets


class Shape(Flag):
    CIRCLE = auto()
    DIAMOND = auto()


class MarkerFactory(object):
    """
    Parameters
    ------------
    shape: Shape enum
        See Shape enum above.

    color: str, QtGui.QColor
        Color of the marker. Marker must be filled and outlined with the
        same color.

    size: int
        Width and height of the output QGraphicsItem

    filled: bool
        Whether to fill the item.
    """

    defaults = {'shape': 'cicle', 'color': QtCore.Qt.red,
                'size': 3, 'filled': True}

    def __init__(self, factory=None, **kwargs):
        if factory is None:
            kwargs = {k: v for k, v in kwargs.items() if k in self.defaults}
            self.__dict__.update(self.defaults)
            self.__dict__.update(kwargs)
        else:
            for k in self.defaults:
                setattr(self, getattr(factory, k))

        self._brush = QtGui.QBrush(self.color)
        self._pen = QtGui.QPen(self.color)

    def _make_circle(self, size):
        return QtGui.QGraphicsEllipseItem(0, 0, size, size)

    def _make_diamond(self, size):
        # define points coordinates from 12 o'clock position, going clockwise
        X = [size / 2, size, size / 2, 0]
        Y = [size, size / 2, 0, size / 2]
        polygon = QtCore.QPolygonF([QtCore.QPointF(x, y) for x, y in zip(X, Y)])
        return QtGui.QGraphicsPolygonItem(polygon)

    def __call__(self):
        if self.shape & Shape.CIRCLE:
            shape = self._make_circle(self.size)
        elif self.shape & Shape.DIAMOND:
            shape = self._make_diamond(self.size)
        else:
            raise TypeError(
                '{} is not available. '.format(self.shape) +
                'Please use one of the shapes available in the Shape enum.')

        if self.filled:
            shape.setBrush(self._brush)
        shape.setPen(self._pen)
        return shape


class VScene(QtWidgets.QGraphicsScene):
    default_image = np.random.randint(0, 256, (512, 512), dtype=np.uint8)

    def __init__(self, groups):
        super().__init__()
        self._group_names = groups
        self._display_default_image()
        self._groups = {k: QtWidgets.QGraphicsItemGroup(self._pixmap)
                        for k in self._group_names}

    def _display_default_image(self):
        """
        Show dummy image to avoid AttributeError when self._pixmap.setPixmap()
        is later called in self.set_pixmap method.
        """
        pixmap = self.array2pixmap(self.default_image)
        self._pixmap = self.addPixmap(pixmap)
        for view in self.views():
            view.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def add_items(self, group, *items):
        for item in items:
            item.setParentItem(self._groups[group])

    def clear_group(self, groups=None):
        if groups is None:
            groups = self._groups.values()
        else:
            groups = [self._groups[k] for k in groups if k in groups]

        children = np.concatenate([grp.childItems() for grp in groups])
        for child in children:
            self.removeItem(child)

    def _rescale_array(self, array):
        # XXX: pixel scaling will eventually be adjustable in the GUI
        min_ = array.min()
        max_ = array.max()
        array = (array - min_) / (max_ - min_) * 256
        return array

    def set_pixmap(self, pixmap):
        rect = self.sceneRect()
        self._pixmap.setPixmap(pixmap)
        self.setSceneRect(rect)

    def array2pixmap(self, array: np.ndarray, rescale=True):
        # https://github.com/sjara/brainmix/blob/master/brainmix/gui/numpy2qimage.py
        if rescale:
            array = self._rescale_array(array)
        array = np.require(array, np.uint8, 'C')
        w, h = array.shape
        qimage = QtGui.QImage(array.data, w, h, QtGui.QImage.Format_Grayscale8)
        return QtGui.QPixmap.fromImage(qimage)

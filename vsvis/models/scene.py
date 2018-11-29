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
from enum import Flag, auto
from qtpy import QtCore, QtGui, QtWidgets
from abc import abstractmethod
from functools import partialmethod
from collections import OrderedDict


class Shape(Flag):
    CIRCLE = auto()
    DIAMOND = auto()


class Dimension(Flag):
    C = auto()
    T = auto()
    Z = auto()


class Marker(object):
    def __init__(self, probability=None):
        self.probability = probability


class DiamondMarker(QtWidgets.QGraphicsPolygonItem, Marker):
    def __init__(self, size, probabilty=None):
        polygon = self._coordinates_setup(size)
        super(QtWidgets.QGraphicsPolygonItem, self).__init__(polygon)
        super(Marker, self).__init__(probabilty)

    def _coordinates_setup(self, size):
        X = [size / 2, size, size / 2, 0]
        Y = [size, size / 2, 0, size / 2]
        return QtCore.QPolygonF([QtCore.QPointF(x, y) for x, y in zip(X, Y)])


class EllipseMarker(QtWidgets.QGraphicsEllipseItem, Marker):
    def __init__(self, size, probabilty=None):
        super(QtWidgets.QGraphicsEllipseItem, self).__init__(0, 0, size, size)
        super(Marker, self).__init__(probabilty)


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

    def __call__(self):
        if self.shape & Shape.CIRCLE:
            marker = EllipseMarker(self.size)
        elif self.shape & Shape.DIAMOND:
            marker = DiamondMarker(self.size)
        else:
            raise TypeError(
                '{} is not available. '.format(self.shape) +
                'Please use one of the shapes available in the Shape enum.')

        if self.filled:
            marker.setBrush(self._brush)
        marker.setPen(self._pen)
        return marker


class ImageManager(object):
    def __init__(self, datasource):
        self._datasource = datasource

    @abstractmethod
    def request(self, index):
        pass


class TiffImageManager(ImageManager, QtCore.QObject):
    """
    dimension: Dimension
        Dimension enum that determines along which axis (channel, time, z)
        to scroll through the image data. Default is time.
    """
    def __init__(self, datasource, dimension=Dimension.T, parent=None):
        super(QtCore.QObject, self).__init__(parent)
        super(ImageManager, self).__init__(datasource)
        self.dimension = dimension
        self._ctz = OrderedDict(
            [(Dimension.C, 0), (Dimension.T, 0), (Dimension.Z, 0)])

    def request(self, index: int) -> np.ndarray:
        self._ctz[self.dimension] = index
        self._datasource.request(*self._ctz.values())


class HDF5ImageManager(ImageManager, QtCore.QObject):
    def __init__(self, datasource: h5py.Dataset, parent=None):
        super(QtCore.QObject, self).__init__(parent)
        super(ImageManager, self).__init__(datasource)

    def request(self, index: int) -> np.ndarray:
        return self._datasource[index, :, :]


class VScene(QtWidgets.QGraphicsScene):
    default_image = np.random.randint(0, 256, (512, 512), dtype=np.uint8)

    def __init__(self, image_manager: ImageManager, groups: OrderedDict):
        super().__init__()
        self._group_names = groups.keys()
        self._display_default_image()
        self._groups = {k: QtWidgets.QGraphicsItemGroup(self._pixmap)
                        for k in self._group_names}
        self._marker_factories = groups.values()
        self._image_manager = image_manager

    def _display_default_image(self):
        """
        Show dummy image to avoid AttributeError when self._pixmap.setPixmap()
        is later called in self.set_pixmap method.
        """
        pixmap = self.array2pixmap(self.default_image)
        self._pixmap = self.addPixmap(pixmap)
        for view in self.views():
            view.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def add_markers(self, group, coordinates, **kwargs):
        for c in coordinates:
            marker_factory = self._marker_factories[group]
            graphics_item = marker_factory()
            graphics_item.setParentItem(self._groups[group])
            graphics_item.setPos(QtCore.QPointF(*c))
        if kwargs:
            group = self._groups[group]
            for attr in kwargs:
                for ch, value in zip(group.childItems(), kwargs[attr]):
                    setattr(ch, attr, value)

    def mask_markers(self, group, function):
        group = self._groups[group]
        for item in group.childItems():
            if function(item):
                item.setVisible(True)
            else:
                item.setVisible(False)

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

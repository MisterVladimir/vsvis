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
from qtpy import QtCore, QtGui, QtWidgets
from abc import abstractmethod
from itertools import repeat
from collections import OrderedDict
from typing import Any, Dict, Sequence, Union
from vladutils.data_structures import EnumDict
from vladutils.iteration import isiterable

from ..enums import Shape, Dimension, DataType


class Marker(object):
    """
    kwargs : Any additional info we want to associate with the marker.
    """
    def __init__(self, **kwargs):
        self.info = kwargs


class DiamondMarker(QtWidgets.QGraphicsPolygonItem, Marker):
    def __init__(self, size, **kwargs):
        polygon = self._coordinates_setup(size)
        QtWidgets.QGraphicsPolygonItem.__init__(self, polygon)
        Marker.__init__(self, **kwargs)

    def _coordinates_setup(self, size):
        X = [size / 2, size, size / 2, 0]
        Y = [size, size / 2, 0, size / 2]
        return QtGui.QPolygonF([QtCore.QPointF(x, y) for x, y in zip(X, Y)])


class EllipseMarker(QtWidgets.QGraphicsEllipseItem, Marker):
    def __init__(self, size, **kwargs):
        QtWidgets.QGraphicsEllipseItem.__init__(self, 0, 0, size, size)
        Marker.__init__(self, **kwargs)


class MarkerFactory(object):
    """
    Parameters
    ------------
    shape: Shape
        See enums.Shape

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

    def __call__(self, x: float, y: float, **kwargs: Any) -> Marker:
        if self.shape & Shape.CIRCLE:
            marker = EllipseMarker(self.size, **kwargs)
        elif self.shape & Shape.DIAMOND:
            marker = DiamondMarker(self.size, **kwargs)
        else:
            raise TypeError(
                '{} is not available. '.format(self.shape) +
                'Please use one of the shapes available in the Shape enum.')

        if self.filled:
            marker.setBrush(self._brush)
        marker.setPen(self._pen)
        marker.setPos(x, y)
        return marker


class GraphicsGroup(QtWidgets.QGraphicsItemGroup):
    def __init__(self, marker_factory: MarkerFactory,
                 parent: Optional[QtGui.QGraphicsItem,
                                  QtWidgets.QGraphicsScene] = None):

        super().__init__(self, parent)
        self._factory = marker_factory

    def add_marker(self, x, y, **kwargs):
        marker = self._factory(x, y, **kwargs)
        marker.setParentItem(parent=self)


# class ImageManager(object):
#     def __init__(self, datasource):
#         self._datasource = datasource

#     @abstractmethod
#     def request(self, index):
#         pass


# class TiffImageManager(ImageManager, QtCore.QObject):
#     """
#     dimension: Dimension
#         Dimension enum that determines along which axis (channel, time, z)
#         to scroll through the image data. Default is time.
#     """
#     def __init__(self, datasource, dimension=Dimension.T, parent=None):
#         super(QtCore.QObject, self).__init__(parent)
#         super(ImageManager, self).__init__(datasource)
#         self.dimension = dimension
#         self._ctz = OrderedDict(
#             [(Dimension.C, 0), (Dimension.T, 0), (Dimension.Z, 0)])

#     def request(self, index: int) -> np.ndarray:
#         self._ctz[self.dimension] = index
#         self._datasource.request(*self._ctz.values())


# class HDF5ImageManager(ImageManager, QtCore.QObject):
#     def __init__(self, datasource: h5py.Dataset, parent=None):
#         super(QtCore.QObject, self).__init__(parent)
#         super(ImageManager, self).__init__(datasource)

#     def request(self, index: int) -> np.ndarray:
#         return self._datasource[index, :, :]


class VScene(QtWidgets.QGraphicsScene):
    """
    factories: EnumDict
        Keys are a DataType enum describing whether we're displaying
        ground truth or predicted markers/data. Values are a MarkerFactory
        that produce's that data's 
    """
    pixmap_set = QtCore.Signal(int)
    buffer_size = 50
    default_image = np.random.randint(0, 256, (512, 512), dtype=np.uint8)

    def __init__(self, factories: Dict[DataType, MarkerFactory],
                 start_index: int = 0):
        super().__init__()
        self._display_default_image()
        self._factories = factories
        self._groups = {}
        self.current_index = start_index

    @QtCore.Property(QtGui.QPixmap)
    def pixmap(self):
        return self._pixmap

    @pixmap.setter
    def pixmap(self, px):
        old = self._pixmap.pixmap()
        rect = None
        if px.width() == old.width() and px.height() == old.height():
            rect = self.sceneRect()
        self._pixmap.setPixmap(px)
        if rect is None:
            rect = self.sceneRect()

        for view in self.views():
            view.fitInView(rect, QtCore.Qt.KeepAspectRatio)

    def getGroups(self):
        return self._groups

    def setGroups(self, groups):
        self._groups = groups

    def resetGroups(self):
        self._groups = {}

    groups = QtCore.Property(
        GraphicsGroup, 'getGroups', 'setGroups', 'resetGroups')

    def _display_default_image(self):
        """
        Show dummy image to avoid AttributeError when self._pixmap.setPixmap()
        is later called in self.set_pixmap method.
        """
        pixmap = self.array2pixmap(self.default_image, rescale=False)
        self._pixmap = self.addPixmap(pixmap)
        for view in self.views():
            view.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def set_markers(self, index: int, dtype: DataType, coordinates: np.ndarray, **kwargs):
        keys = list(self._groups.keys())
        try:
            groups = self._groups[index]
        except:
            # mf = MarkerFactory
            groups = EnumDict([(k, GraphicsGroup(mf, self.pixmap))
                               for k, mf in self._factories.items()])
            self._groups[index] = groups

        if len(keys) > self.buffer_size:
            # if we've added more groups than is allowed in the buffer,
            # remove a random 10% of the items in the buffer
            n = int(0.1 * len(keys))
            removed_indices = np.random.choice(keys, n)
            for i in removed_indices:
                # remove markers
                for g in self._groups[i].values():
                    self.removeItem(g)
                del self._groups[i]

        group = groups[dtype]
        assert coordinates.shape[1] == 2
        n = coordinates.shape[0]
        assert all([n == len(v) for v in kwargs.values() if isiterable(v)])
        kwargs = {k: iter(v) if isiterable(v) else repeat(v)
                  for k, v in kwargs.items()}
        for c in coordinates:
            kw = {k: next(v) for k, v in kwargs.items()}
            group.add_marker(*c, **kw)
            # group.setVisible(False)

    def get_markers(self, index: int, dtype: DataType):
        group = self._groups[index][dtype]
        return group.childItems()

    def set_markers_visible(
            self, index: int, dtype: DataType, visible: bool,
            item_index: Union[slice, Sequence[int], int] = slice(None)):

        markers = self.get_markers(index, dtype)
        if isiterable(item_index):
            for i in item_index:
                markers[i].setVisible(visible)
        else:
            for m in markers[item_index]:
                m.setVisible(visible)

    @staticmethod
    def rescale_array(array):
        # XXX: pixel scaling will eventually be adjustable in the GUI
        min_ = array.min()
        max_ = array.max()
        array = (array - min_) / (max_ - min_) * 256
        return array

    @staticmethod
    def array2pixmap(array: np.ndarray, rescale=True) -> QtGui.QPixmap:
        # https://github.com/sjara/brainmix/blob/master/brainmix/gui/numpy2qimage.py
        if rescale:
            array = VScene.rescale_array(array)
        array = np.require(array, np.uint8, 'C')
        w, h = array.shape
        qimage = QtGui.QImage(array.data, w, h, QtGui.QImage.Format_Grayscale8)
        return QtGui.QPixmap.fromImage(qimage)

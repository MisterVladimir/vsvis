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
from abc import abstractmethod
from typing import Any, Optional, Union
from functools import partialmethod
from qtpy.QtCore import QObject, QPointF, QRectF, Qt, Property
from qtpy.QtGui import QBrush, QColor, QPen, QPainter, QPolygonF
from qtpy.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsItem, QGraphicsPolygonItem,
    QStyleOptionGraphicsItem, QWidget)
from vladutils.data_structures import EnumDict

from ..config import Shape


class Marker(object):
    """
    This is a mix-in class that provides convenience setters and getters
    common to all GraphicsItem sibling classes. This class also allows us
    to store any useful info, e.g. marker coordinates, in the 'info' attribute.

    Arguments
    -----------
    parent : VGraphicsGroup
        Must be a VGraphicsGroup and not a parent class, e.g. QGraphicsItem.

    kwargs : Any
        Additional info we want to associate with the marker.
    """
    def __init__(self, key: Optional[int] = None, **kwargs: Any):
        self.info = kwargs
        self.key = key

    def set_marker_color(self, color: Union[QColor, int]):
        color = QColor(color)
        pen = QPen(color)
        brush = QBrush(color)
        self.setPen(pen)
        self.setBrush(brush)

    def get_marker_color(self):
        """
        Marker color.
        """
        return self.pen().color()

    def get_marker_fill(self) -> bool:
        """
        Whether this marker is filled in or merely an outline.
        """
        return bool(self.brush().style())

    def set_marker_fill(self, f: bool):
        if f:
            f = Qt.SolidPattern
        else:
            f = Qt.NoBrush
        self.brush().setStyle(f)

    @abstractmethod
    def _not_implemented(self, *args, **kwargs):
        raise NotImplementedError(
            'This property should be implemented in a co-inherited class '
            'higher up in the method resolution order.')

    get_marker_size = partialmethod(_not_implemented)
    set_marker_size = partialmethod(_not_implemented)

    pen = partialmethod(_not_implemented)
    setPen = partialmethod(_not_implemented)
    brush = partialmethod(_not_implemented)
    setBrush = partialmethod(_not_implemented)


_marker_docstring = \
    """
    Note that instances of this class are not meant to be instantiated
    directly. Instead, they are generated by calling an instance of
    MarkerFactory. Use the setters and getters for 'size', 'color',
    and 'filled' to modify the eponymous properties.

    Arguments
    -----------
    parent : VGraphicsGroup
        See documentation for QGraphicsItem

    size: int
        Width and height, in pixels(?).
    """


class DiamondMarker(QGraphicsPolygonItem, Marker):
    __doc__ = _marker_docstring

    def __init__(self, size: int, key: Optional[int] = None, **kwargs):
        polygon = self._make_polygon(size)
        self._size = size
        QGraphicsPolygonItem.__init__(self, polygon, parent=None)
        Marker.__init__(self, key, **kwargs)

    def _make_polygon(self, size):
        X = [size / 2, size, size / 2, 0]
        Y = [size, size / 2, 0, size / 2]
        return QPolygonF([QPointF(x, y) for x, y in zip(X, Y)])

    def get_marker_size(self) -> int:
        return self._size

    def set_marker_size(self, size: int):
        polygon = self._make_polygon(size)
        self.setPolygon(polygon)
        self._size = size


class EllipseMarker(QGraphicsEllipseItem, Marker):
    __doc__ = _marker_docstring

    def __init__(self, size: int, key: Optional[int] = None, **kwargs):
        QGraphicsEllipseItem.__init__(self, 0, 0, size, size)
        Marker.__init__(self, key, **kwargs)

    def get_marker_size(self):
        return self.rect().width()

    def set_marker_size(self, sz: int):
        self.setRect(0, 0, sz, sz)


class TunableMarker(QGraphicsItem):
    def __init__(self, shape: Shape, size: int,
                 key: Optional[int] = None, **kwargs):
        super().__init__()
        self._shape = shape
        self._size = size
        self.key = key
        self.info = kwargs

        self._pen = QPen()
        self._pen.setWidthF(0.25)
        self._brush = QBrush()

    def _make_rect(self, length):
        # make a rectangle of width and height equal to 'length' and centered
        # about (0, 0)
        return QRectF(-length / 2, -length / 2, length, length)

    def boundingRect(self):
        return self._make_rect(self._size + 4)

    def _paint_ellipse(self, painter):
        rect = self._make_rect(self._size)
        painter.drawEllipse(rect)

    def _paint_diamond(self, painter):
        size = self._size
        X = [0, size / 2, 0, -size / 2, 0]
        Y = [size / 2, 0, -size / 2, 0, size / 2]
        points = [QPointF(x, y) for x, y in zip(X, Y)]
        polygon = QPolygonF(points)
        painter.drawPolygon(polygon, len(points))

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
              widget: QWidget):

        painter.setPen(self._pen)
        painter.setBrush(self._brush)

        shape_to_paint_method = {Shape.CIRCLE: self._paint_ellipse,
                                 Shape.DIAMOND: self._paint_diamond}
        drawing_method = shape_to_paint_method[self._shape]
        drawing_method(painter)

    def get_marker_color(self):
        """
        Marker color.
        """
        return self._pen.color()

    def set_marker_color(self, color: Union[QColor, int]):
        color = QColor(color)
        self._pen.setColor(color)
        self._brush.setColor(color)
        self.update()

    def get_marker_fill(self) -> bool:
        """
        Whether this marker is filled in or merely an outline.
        """
        return bool(self._brush.style())

    def set_marker_fill(self, f: bool):
        if f:
            f = Qt.SolidPattern
        else:
            f = Qt.NoBrush
        self._brush.setStyle(f)
        self.update()

    def get_marker_shape(self):
        return self._shape

    def set_marker_shape(self, shape: Shape):
        self._shape = shape
        self.update()

    def get_marker_size(self):
        return self._size

    def set_marker_size(self, sz: int):
        self._size = sz
        self.update()


class MarkerFactory(QObject):
    """
    Parameters
    ------------
    shape: Shape
        See config.Shape

    color: str, QColor
        Color of the marker. Marker must be filled and outlined with the
        same color.

    size: int
        Width and height of the output QGraphicsItem

    filled: bool
        Whether to fill the item.
    """
    _shape_to_class = EnumDict([(Shape.CIRCLE, EllipseMarker),
                                (Shape.DIAMOND, DiamondMarker)])

    def __init__(self, shape=Shape.CIRCLE, color=Qt.red, size=3,
                 filled=True):
        super().__init__()
        self._brush = QBrush()
        self._pen = QPen()

        self.set_marker_shape(shape)
        self.set_marker_size(size)
        self.set_marker_color(color)
        self.set_marker_fill(filled)

    def get_marker_color(self) -> QColor:
        return self._pen.color()

    def set_marker_color(self, color: Union[QColor, int]):
        # XXX: what's the difference between settning alpha to 0 and
        # passing Qt.NoBrush to the constructor?
        # filled = deepcopy(self._brush.style())
        self._pen.setColor(color)
        self._brush.setColor(color)
        # self._brush.setStyle(filled)

    def get_marker_fill(self) -> bool:
        return bool(self._brush.style())

    def set_marker_fill(self, f: bool):
        if f:
            style = Qt.SolidPattern
        else:
            style = Qt.NoBrush
        self._brush.setStyle(style)

    def get_marker_shape(self) -> Shape:
        return self._shape

    def set_marker_shape(self, shape: Shape):
        self._shape = shape

    def get_marker_size(self):
        return self._size

    def set_marker_size(self, size: int):
        self._size = size

    def __call__(self, x: float, y: float, **kwargs: Any) -> Marker:
        """
        Create a Marker with the properties specified by this Factory.

        Parameters
        ------------
        x : float
        y : float
            X, Y coordinates of the marker.

        key : int
            Index that this marker will have in the parent VGraphicsGroup.
        """
        marker = TunableMarker(self._shape, self._size, key=None, **kwargs)
        marker.set_marker_color(self.get_marker_color())
        marker.set_marker_fill(self.get_marker_fill())
        # marker = self._marker_class(self._size, **kwargs)
        # marker.setBrush(self._brush)
        # marker.setPen(self._pen)
        marker.setPos(x, y)
        return marker

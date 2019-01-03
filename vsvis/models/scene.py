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
from copy import deepcopy
from qtpy.QtCore import QObject, Qt, Property, Signal
from qtpy.QtGui import QColor, QImage, QPixmap
from qtpy.QtWidgets import QGraphicsItem, QGraphicsItemGroup, QGraphicsScene
from itertools import repeat
from functools import partialmethod, reduce
from collections import OrderedDict
from typing import Generator, Iterable, List, Optional, Sequence, TypeVar, Union
from vladutils.data_structures import EnumDict
from vladutils.iteration import isiterable

from .marker import Marker, MarkerFactory
from ..config import DataType, MarkerVisible, DATATYPES

VGroupType = TypeVar('VGroupType', bound='VGraphicsGroup')
VSceneType = TypeVar('VSceneType', bound='VSceneType')
ParentGraphicsType = Union[VGroupType, QGraphicsItem]
ChildGraphicsType = Union[VGroupType, Marker]


class VGraphicsGroup(QGraphicsItemGroup):
    """
    It is the parentItem's responsibility to add this child (1) to the
    QGraphicsScene and (2) to its children.

    Parameters
    ------------
    parent : Union[VGraphicsGroup, VGraphicsScene]
    key : int
        Only required if parent is a VGraphicsGroup, in which case this will be
        the index 
    """
    def __init__(self, key: Union[int, None], dtype: DataType = None):
        self.key = key
        self._dtype = dtype
        super().__init__()

        # _child_keys contains private set of indices used to fetch child Items
        self._child_items = dict()

    def __repr__(self):
        return '{}: #{} <parent: {}>'.format(self.__class__, self.key, self.parentItem())

    def __iter__(self):
        return iter(self._child_items.values())

    def __getitem__(self, index: Union[int, slice, Iterable[int]]) -> List[ChildGraphicsType]:
        """
        Note this interface is different from that of a list or dict: it will
        return a list whether the 'index' argument is an int, a slice, or an
        iterable containing int.
        """
        if isinstance(index, int):
            return self._child_items[index]
        elif isinstance(index, slice):
            start, stop, step = index.indices(max(self._child_items) + 1)
            keys = set(range(start, stop, step))
            keys.intersection_update(self._child_items)
            return [self._child_items[k] for k in sorted(list(keys))]
        elif isinstance(index, Iterable):
            index = sorted(list(index))
            return [self._child_items[i] for i in index]

    def __len__(self):
        return len(self._child_items)

    def __setitem__(self, key: int, value: ChildGraphicsType):
        self.add_child_item(value, key, True)

    def __contains__(self, key: int):
        return key in self._child_items

    def keys(self):
        return sorted(list(self._child_items.keys()))

    def values(self):
        keys = self.keys()
        return [self._child_items[k] for k in keys]

    def items(self):
        keys = self.keys()
        values = (self._child_items[k] for k in keys)
        return list(zip(keys, values))

    def replace_child_items(self, items: Iterable[ChildGraphicsType],
                            vis: Optional[bool] = False) -> Union[int, bool]:
        """
        Removes all children of this GraphicsItemGroup, and adds the list of
        GraphicsItems that was passed in.

        vis : Optional[bool]
            Whether items should be visible in the QGraphicsScene.

        Returns
        --------
        True if no exceptions occured.
        False if a marker could not be added.
        int 'index' if child item at position 'index' could not be removed.
        """
        scene = self.scene()
        for index, child in self.items():
            scene.removeItem(child)
            del self._child_items[index]

        for index, item in enumerate(items):
            item.key = index
            item.setVisible(vis)
            scene.addItem(item)
            item.setParentItem(self)
            self._child_items[index] = item

        return True

    def add_subgroup(self, key: Optional[int] = None, overwrite: bool = True) -> int:
        """
        Convenience method that adds a VGraphicsGroup as a child. This can be
        just as easily achieved using the add_child_item method directly.
        """
        subgroup = VGraphicsGroup(key)
        return self.add_child_item(subgroup, key, overwrite)

    def add_child_item(self, item, key: Optional[int] = None, overwrite: bool = True) -> int:
        if key is not None:
            # doublecheck if there's already an item at the given index
            if key in self._child_items and not overwrite:
                raise Exception('Cannot overwrite item at key {}'.format(
                    key))
            else:
                self.delete_child_item(key)
        elif self._child_items.keys():
            key = max(self._child_items.keys()) + 1
        else:
            key = 0

        # un-parent from current parent
        oldparent = item.parentItem()
        if isinstance(oldparent, VGraphicsGroup):
            _ = oldparent.pop_child_item(item.key)

        item.setParentItem(self)
        item.key = key
        self._child_items[key] = item
        return key

    def pop_child_item(self, index: int) -> Union[QGraphicsItem, None]:
        """
        Re-parents a GraphicsItem from its current parentItem to its
        QGraphicsScene, and returns it. Also removes it from any non-PyQt
        containers. If no child exists at index, return None.
        """
        child = self._child_items.pop(index, None)
        if child is not None:
            # reparent child to the VGraphicsScene
            child.setParentItem(0)
            return child

    def delete_child_item(self, index: int) -> bool:
        """
        Destroys a child item at index.
        """
        child = self._child_items.pop(index, None)
        if child is not None:
            scene = self.scene()
            scene.removeItem(child)

    def clear(self):
        """
        Destroys all children.
        """
        subgroups = (sg for sg in self._child_items.values()
                     if isinstance(sg, VGraphicsGroup))
        for group in subgroups:
            group.clear()

        markers = (m for m in self._child_items.values()
                   if isinstance(m, Marker))
        if markers:
            scene = self.scene()
            for m in markers:
                scene.removeItem(m)

        self._child_items = dict()

    @Property(object)
    def dtype(self) -> DataType:
        if self._dtype is None:
            return self.parentItem().dtype
        else:
            return self._dtype

    @dtype.setter
    def dtype(self, dtype: DataType):
        parent = self.parentItem()
        if isinstance(parent, VGraphicsGroup):
            raise NotImplementedError(
                'dtype is already set by the parentItem, {}.'.format(parent))
        else:
            self._dtype = dtype

    @Property(bool)
    def is_toplevel_group(self):
        return self.key is None

    def _set_marker_property(self, getter_name, setter_name, marker, value):
        getter = getattr(marker, getter_name)
        if not value == getter(marker):
            for ch in self._child_items:
                setter = getattr(ch, setter_name)
                setter(value)
            if not isinstance(self.parentItem(), VGraphicsGroup):
                setter = getattr(marker, setter_name)
                setter(value)

    set_marker_color = partialmethod(
        _set_marker_property, 'get_marker_color', 'set_marker_color')
    set_marker_fill = partialmethod(
        _set_marker_property, 'get_marker_fill', 'set_marker_fill')
    set_marker_size = partialmethod(
        _set_marker_property, 'get_marker_size', 'set_marker_size')

    def _get_marker_property(self, getter_name, marker):
        getter = getattr(marker, getter_name)
        return getter()

    get_marker_color = partialmethod(_get_marker_property, 'get_marker_color')
    get_marker_fill = partialmethod(_get_marker_property, 'get_marker_fill')
    get_marker_size = partialmethod(_get_marker_property, 'get_marker_size')
    get_marker_shape = partialmethod(_get_marker_property, 'get_marker_shape')


class VGraphicsScene(QGraphicsScene):
    """
    Note that is the responsibility of a Controller-type object to coordinate
    the display of markers appropriate to the image.

    factories: EnumDict
        Keys are a DataType enum describing whether we're displaying
        ground truth or predicted markers/data. Values are a MarkerFactory
        that produce's that data's 
    """
    buffer_size = 50
    default_image = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
    pixmap_changed = Signal(int)
    markers_changed = Signal(int, object)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._display_default_image()

        self._groups = dict()
        self.current_index = 0

    def _display_default_image(self):
        """
        Show dummy image to avoid AttributeError when self._pixmap.setPixmap()
        is called (see setter function of self.pixmap).
        """
        pixmap = self.array2pixmap(self.default_image, rescale=False)
        self._pixmap = self.addPixmap(pixmap)
        for view in self.views():
            view.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    @Property('QPixmap')
    def pixmap(self):
        return self._pixmap

    @pixmap.setter
    def pixmap(self, dummy):
        raise NotImplementedError('Use the set_pixmap method instead.')

    def set_pixmap(self, px: np.ndarray, index: int):
        """
        If 'px' is the same size as the previous image -- e.g. another image
        channel or frame in a time series -- propagate the same level of zoom.
        """
        old = self._pixmap.pixmap()
        w, h = old.width(), old.height()
        self._pixmap.setPixmap(px)

        if not (px.width() == w and px.height() == h):
            # https://www.qtcentre.org/threads/20091-Position-in-a-QPixMap-created-from-a-QGraphicsScene?p=98862#post98862
            rect = self._pixmap.sceneBoundingRect()
            self.setSceneRect(rect)
        # XXX: if size has not changed, not sure we should be calling fit_to_window
        for view in self.views():
            view.fit_to_window()

        self.pixmap_changed.emit(index)

    @staticmethod
    def rescale_array(array):
        # XXX: pixel scaling will eventually be adjustable in the GUI
        min_ = array.min()
        max_ = array.max()
        array = (array - min_) / (max_ - min_) * 256
        return array

    @staticmethod
    def array2pixmap(array: np.ndarray, rescale: bool = True) -> QPixmap:
        # https://github.com/sjara/brainmix/blob/master/brainmix/gui/numpy2qimage.py
        if rescale:
            array = VGraphicsScene.rescale_array(array)
        array = np.require(array, np.uint8, 'C')
        w, h = array.shape
        qimage = QImage(array.data, w, h, QImage.Format_Grayscale8)
        return QPixmap.fromImage(qimage)

    @Property(object)
    def groups(self):
        return self._groups

    def add_top_level_group(self, dtype: DataType):
        """
        Sets a top-level group associated with 'dtype'-type data. Child Groups
        must be set with the Group's methods.
        """
        group = VGraphicsGroup(None, dtype)
        group.setParentItem(self.pixmap)
        # self.addItem(group)
        self._groups[dtype] = group

    def delete_top_level_group(self, dtype: DataType):
        keys = (k for k in self._groups if k & dtype)
        for k in keys:
            group = self._groups[dtype]
            self.removeItem(group)
            del self._groups[dtype]

    def clear_top_level_group(self, dtype: DataType):
        """
        Removes all markers from VGraphicsGroup children (and their children, etc.) from
        top-level VGraphicsGroup associated with a DataType parameter. Note
        that this does not remove 
        """
        keys = (k for k in self._groups if k & dtype)
        for k in keys:
            self._groups[k].clear()

    def has_markers(self, dtype: DataType,
                    index: Optional[int] = None) -> Union[bool, List[int]]:
        """
        Tests for the existence of a VGraphicsGroup in this Scene.

        To test for the existence of a top-level group, set 'index' paramter to
        None.
        """
        if index is None:
            return dtype in self._groups
        else:
            group = self._groups[dtype]

        try:
            subgroup = group[index]
        except KeyError:
            return False
        else:
            return subgroup.keys()

    def get_markers(
            self, dtype: DataType, index: int,
            visible: MarkerVisible = MarkerVisible.either) -> Sequence[Marker]:

        try:
            group = self._groups[dtype]
        except KeyError:
            # dummy expression to keep the return type consistent
            return []
        else:
            # note that each member of the 'groups' generator is a list
            if not visible ^ MarkerVisible.either:
                return group[index][slice(None)]
            elif visible & MarkerVisible.true:
                return [m for m in group[index] if m.isVisible()]
            elif visible & MarkerVisible.false:
                return [m for m in group[index] if not m.isVisible()]

    def reset_markers(self, dtype: DataType, index: int,
                      markers: Iterable[Marker], vis: bool = False) -> bool:
        """
        Deletes existing Markers and adds new Markers with the passed-in
        coordinates.
        """
        if dtype in self._groups:
            group = self._groups[dtype]
        else:
            raise KeyError('{} top level group not created.'.format(
                repr(dtype)))

        try:
            subgroup = group[index]
        except KeyError:
            subgroup = VGraphicsGroup(index, dtype)
            subgroup.setParentItem(group)
        finally:
            return subgroup.replace_child_items(markers, vis)

    def delete_markers(self, dtype: DataType,
                       index: Union[int, slice, Sequence[int]]) -> bool:
        """
        Delete all child items from a VGraphicsGroup.
        """
        try:
            group = self._groups[dtype][index]
        except KeyError:
            return False
        else:
            for k in group.keys():
                group.delete_child_item(k)
            # self.markers_changed.emit(index, dtype)
            return True

    def set_markers_visible(
            self, dtype: DataType, index: int, visible: bool,
            mindex: Union[int, slice, Iterable[int]] = slice(None)) -> bool:
        """
        Parameters
        ------------
        dtype : DataType

        index : int
            Group index.

        visible : bool
            Whether to make the marker visible (=True) or invisible (=False).

        mindex : Union[int, slice, Iterable[int]]
            Marker index within the Group.

        Returns
        ------------
        success : bool
            Whether the markers were successfully added, i.e. returns False if
            there is no VMarkerGroup at index, 'index'. Returns True unless
            another exception is encountered.
        """
        print('getting group: {}'.format(repr(dtype)))
        print('mindex: {}'.format(mindex))
        group = self._groups[dtype]
        try:
            subgroup = group[index]
        except KeyError:
            return False
        else:
            print('subgroup: {}'.format(subgroup))
            if isinstance(mindex, int):
                marker = subgroup[mindex]
                marker.setVisible(visible)
            else:
                for marker in subgroup[mindex]:
                    marker.setVisible(visible)
            return True

    def count_markers(self, dtype: DataType, index: int) -> Union[bool, int]:
        if dtype in self._groups:
            group = self._groups[dtype]
        else:
            return False

        if index in group:
            return len(group[index])
        else:
            return False

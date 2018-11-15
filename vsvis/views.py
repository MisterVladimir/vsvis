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
import pickle
from PyQt5 import QtCore, QtGui, QtWidgets
from collections import namedtuple
from io import BytesIO


class DropListView(QtWidgets.QListView):
    mime_type = ('application/x-qabstractitemmodeldatalist',
                 'application/node')

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        # self.setDragEnabled(False)
        # self.setAcceptDrops(True)
        # self.setDropIndicatorShown(True)

    def _filter_event(self, event):
        data = event.mimeData()
        correct_type = any([data.hasFormat(typ) for typ in self.mime_type])
        print("type correct: {}".format(correct_type))
        print("type is: {}".format(event.mimeData().formats()))
        correct_source = event.source() in self.sources()
        print("source correct: {}".format(correct_source))

        if correct_type and correct_source:
            return data
        else:
            return False

    def set_drop_sources(self, *sources):
        self._drop_sources = sources

    def sources(self):
        return self._drop_sources

    def dragEnterEvent(self, event):
        print('entered')
        if self._filter_event(event):
            event.acceptProposedAction()
            print('drag accepted')
        else:
            print('drag not accepted')
            print('source: {}'.format(event.source()))
            print('type: {}'.format(event.mimeData().formats()))
            super().dropEvent(event)

    def dragMoveEvent(self, event):
        print('moving')
        super().dragMoveEvent(event)

    def dropEvent(self, event):
        print('dropped')
        data = self._filter_event(event)
        if data:
            print('drop accepted')
            event.acceptProposedAction()
        else:
            print('drop not accepted')
            super().dropEvent(event)


class DragTreeView(QtWidgets.QTreeView):
    NodeInfo = namedtuple('NodeInfo', ['name', 'path'])

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_start_position = None

    def _encode_nodes(self, nodes):
        # namedtuple masquerading as Node with the relevant info
        node_info = [self.NodeInfo(node.name, node.path) for node in nodes]
        byte = BytesIO()
        pickle.dump(node_info, byte)
        byte.seek(0)
        qbyte = QtCore.QByteArray(byte.read())
        mime = QtCore.QMimeData()
        mime.setData('application/node', qbyte)
        return mime

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # if event.button() == QtCore.Qt.LeftButton and :
            # self.drag_start_position = None
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if not event.buttons() == QtCore.Qt.LeftButton or self.drag_start_position is None:
            super().mouseMoveEvent(event)
            return
        dist = (event.pos() - self.drag_start_position).manhattanLength()
        if dist < QtWidgets.QApplication.startDragDistance():
            super().mouseMoveEvent(event)
            return

        model = self.model()
        nodes = [model.getNode(index) for index in self.selectedIndexes()]
        data = self._encode_nodes(nodes)
        drag = QtGui.QDrag(self)
        drag.setMimeData(data)
        action = drag.exec_()
        self.drag_start_position = None

        super().mouseMoveEvent(event)

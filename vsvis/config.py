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
import os
from qtpy.QtGui import QIcon
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGraphicsItem, QGraphicsScene
from qtpy.uic import loadUiType as _loadUiType
from functools import partial
from enum import IntFlag, auto
from typing import Union
from vladutils.data_structures import EnumDict


loadUiType = partial(_loadUiType, from_imports=True, import_from='vsvis')


# enumerations used throughout the program
class DataType(IntFlag):
    GROUND_TRUTH = auto()
    PREDICTED = auto()
    HDF_IMAGE = auto()
    TIFF_IMAGE = auto()

    DATA = PREDICTED | GROUND_TRUTH
    HD5 = GROUND_TRUTH | PREDICTED | HDF_IMAGE
    IMAGE = HDF_IMAGE | TIFF_IMAGE


def MarkerType(IntFlag):
    TOPLEVEL = auto()
    SUBGROUP = auto()
    MARKER = auto()


class Shape(IntFlag):
    CIRCLE = auto()
    DIAMOND = auto()
    ANY = CIRCLE | DIAMOND


class Dimension(IntFlag):
    C = auto()
    T = auto()
    Z = auto()


class MarkerVisible(IntFlag):
    true = auto()
    false = auto()
    either = true | false


MARKER_ICONS = EnumDict([(Shape.CIRCLE, QIcon(':/circle')),
                         (Shape.DIAMOND, QIcon(':/diamond'))])

DEFAULT_MARKER_PARAMETERS = dict(shape=Shape.CIRCLE, size=3,
                                 color=Qt.white, filled=True)

EXTENSIONS = EnumDict([(DataType.HD5, ['.h5', '.hdf5', '.hf5', '.hd5']),
                       (DataType.TIFF_IMAGE, ['.tif', '.tiff', '.ome.tif'])])

FILETYPES = EnumDict([(DataType.HD5, 'HDF5 Files'),
                      (DataType.TIFF_IMAGE, 'Tiff Files')])

NAMES = dict([(DataType.GROUND_TRUTH, 'Ground Truth'),
              (DataType.PREDICTED, 'Predicted')])

DATAPARAM = dict([(DataType.GROUND_TRUTH, ['X', 'Y']),
                  (DataType.PREDICTED, ['X', 'Y', 'Probability'])])

DATATYPES = [DataType.GROUND_TRUTH, DataType.PREDICTED]

# NAME = EnumDict([(, ),
#                  (, )])


# https://stackoverflow.com/questions/25389095/python-get-path-of-root-project-structure
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(ROOT_DIR, 'ui')
TEST_DIR = os.path.join(ROOT_DIR, 'tests')

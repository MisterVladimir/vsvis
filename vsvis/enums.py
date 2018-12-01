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
from enum import Flag, auto


class DataType(Flag):
    GROUND_TRUTH = auto()
    PREDICTED = auto()
    HDF_IMAGE = auto()
    TIFF_IMAGE = auto()

    DATA = PREDICTED | GROUND_TRUTH
    HD5 = GROUND_TRUTH | PREDICTED | HDF_IMAGE
    IMAGE = HDF_IMAGE | TIFF_IMAGE


class Shape(Flag):
    CIRCLE = auto()
    DIAMOND = auto()


class Dimension(Flag):
    C = auto()
    T = auto()
    Z = auto()

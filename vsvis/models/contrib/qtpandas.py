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
import pandas as pd
import numpy as np

from qtpy.QtCore import (QAbstractTableModel, QDateTime, QModelIndex,
                         QObject, Qt, Signal, Slot)
from typing import Optional


DTYPE_ROLE = Qt.UserRole + 1
DATAFRAME_ROLE = Qt.UserRole + 2
DTYPE_CHANGE_ROLE = Qt.UserRole + 3


class SupportedDtypesTranslator(QObject):
    """Represents all supported datatypes and the translations (i18n).

    """
    def __init__(self, parent=None):
        """Constructs the object with the given parent.

        Args:
            parent (QObject, optional): Causes the objected to be owned
                by `parent` instead of Qt. Defaults to `None`.

        """
        super(SupportedDtypesTranslator, self).__init__(parent)

        # we are not supposed to use str objects (str/ dtype('S'))
        self._strs = [(np.dtype(object), self.tr('text'))]

        self._ints = [(np.dtype(np.int8), self.tr('small integer (8 bit)')),
                      (np.dtype(np.int16), self.tr('small integer (16 bit)')),
                      (np.dtype(np.int32), self.tr('integer (32 bit)')),
                      (np.dtype(np.int64), self.tr('integer (64 bit)'))]

        self._uints = [(np.dtype(np.uint8), self.tr('unsigned small integer (8 bit)')),
                       (np.dtype(np.uint16), self.tr('unsigned small integer (16 bit)')),
                       (np.dtype(np.uint32), self.tr('unsigned integer (32 bit)')),
                       (np.dtype(np.uint64), self.tr('unsigned integer (64 bit)'))]

        self._floats = [(np.dtype(np.float16), self.tr('floating point number (16 bit)')),
                      (np.dtype(np.float32), self.tr('floating point number (32 bit)')),
                      (np.dtype(np.float64), self.tr('floating point number (64 bit)'))]

        self._datetime = [(np.dtype('<M8[ns]'), self.tr('date and time'))]

        self._bools = [(np.dtype(bool), self.tr('true/false value'))]

        self._all = self._strs + self._ints + self._uints + self._floats + self._bools + self._datetime

    def strTypes(self):
        """Concatenates datatypes into a list.

        Returns:
            list: List of supported string datatypes.

        """
        return [dtype for (dtype, _) in self._strs]

    def intTypes(self):
        """Concatenates datatypes into a list.

        Returns:
            list: List of supported interger datatypes.

        """
        return [dtype for (dtype, _) in self._ints]

    def uintTypes(self):
        """Concatenates datatypes into a list.

        Returns:
            list: List of supported unsigned integer datatypes.

        """
        return [dtype for (dtype, _) in self._uints]

    def floatTypes(self):
        """Concatenates datatypes into a list.

        Returns:
            list: List of supported float datatypes.

        """
        return [dtype for (dtype, _) in self._floats]

    def boolTypes(self):
        """Concatenates datatypes into a list.

        Returns:
            list: List of supported boolean datatypes.

        """
        return [dtype for (dtype, _) in self._bools]

    def datetimeTypes(self):
        """Concatenates datatypes into a list.

        Returns:
            list: List of supported datetime datatypes.

        """
        return [dtype for (dtype, _) in self._datetime]

    def allTypes(self):
        """Concatenates datatypes into a list.

        Returns:
            list: List of all supported datatypes.

        """
        return [dtype for (dtype, _) in self._all]


    def description(self, value):
        """Fetches the translated description for the given datatype.

        The given value will be converted to a `numpy.dtype` object, matched
        against the supported datatypes and the description will be translated
        into the preferred language. (Usually a settings dialog should be
        available to change the language).

        If the conversion fails or no match can be found, `None` will be returned.

        Args:
            value (type|numpy.dtype): Any object or type.

        Returns:
            str: The translated description of the datatype
            None: If no match could be found or an error occured during convertion.

        """
        # lists, tuples, dicts refer to numpy.object types and
        # return a 'text' description - working as intended or bug?
        try:
            value = np.dtype(value)
        except TypeError as e:
            return None
        for (dtype, string) in self._all:
            if dtype == value:
                return string

        # no match found return given value
        return None

    def dtype(self, value):
        """Gets the datatype for the given `value` (description).

        Args:
            value (str): A text description for any datatype.

        Returns:
            numpy.dtype: The matching datatype for the given text.
            None: If no match can be found, `None` will be returned.

        """
        for (dtype, string) in self._all:
            if string == value:
                return dtype

        return None

    def names(self):
        """Fetches all descriptions for the datatypes.

        Returns:
            list: A list of all datatype descriptions.

        """
        return [string for (_, string) in self._all]

    def tupleAt(self, index):
        """Gets the tuple (datatype, description) at the given position out of all supported types.

        Args:
            index (int): An index to access the list of supported datatypes.

        Returns:
            tuple: A tuple consisting of the (datatype, description) will be
                returned, if the index is valid. If not, an empty tuple is returned.

        """
        try:
            return self._all[index]
        except IndexError as e:
            return ()


SupportedDtypes = SupportedDtypesTranslator()


class ColumnDtypeModel(QAbstractTableModel):
    """Data model returning datatypes per column

    Attributes:
        dtypeChanged (Signal(columnName)): emitted after a column has changed it's data type.
        changeFailed (Signal('QString')): emitted if a column
            datatype could not be changed. An errormessage is provided.
    """
    dtypeChanged = Signal(int, object)
    changeFailed = Signal('QString', QModelIndex, object)

    def __init__(self, dataFrame=None, editable=False):
        """the __init__ method.

        Args:
            dataFrame (pandas.core.frame.DataFrame, optional): initializes the model with given DataFrame.
                If none is given an empty DataFrame will be set. defaults to None.
            editable (bool, optional): apply changes while changing dtype. defaults to True.

        """
        super(ColumnDtypeModel, self).__init__()
        self.headers = ['column', 'data type']

        self._editable = editable

        self._dataFrame = pd.DataFrame()
        if dataFrame is not None:
            self.setDataFrame(dataFrame)

    def dataFrame(self):
        """getter function to _dataFrame. Holds all data.

        Note:
            It's not implemented with python properties to keep Qt conventions.

        """
        return self._dataFrame

    def setDataFrame(self, dataFrame):
        """setter function to _dataFrame. Holds all data.

        Note:
            It's not implemented with python properties to keep Qt conventions.

        Raises:
            TypeError: if dataFrame is not of type pandas.core.frame.DataFrame.

        Args:
            dataFrame (pandas.core.frame.DataFrame): assign dataFrame to _dataFrame. Holds all the data displayed.

        """
        if not isinstance(dataFrame, pd.core.frame.DataFrame):
            raise TypeError('Argument is not of type pandas.DataFrame')

        self.layoutAboutToBeChanged.emit()
        self._dataFrame = dataFrame
        self.layoutChanged.emit()

    def editable(self):
        """getter to _editable """
        return self._editable

    def setEditable(self, editable):
        """setter to _editable. apply changes while changing dtype.

        Raises:
            TypeError: if editable is not of type bool.

        Args:
            editable (bool): apply changes while changing dtype.

        """
        if not isinstance(editable, bool):
            raise TypeError('Argument is not of type bool')
        self._editable = editable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """defines which labels the view/user shall see.

        Args:
            section (int): the row or column number.
            orientation (Qt.Orienteation): Either horizontal or vertical.
            role (Qt.ItemDataRole, optional): Defaults to `Qt.DisplayRole`.

        Returns
            str if a header for the appropriate section is set and the requesting
                role is fitting, None if not.

        """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            try:
                return self.headers[section]
            except (IndexError, ):
                return None

    def data(self, index, role=Qt.DisplayRole):
        """Retrieve the data stored in the model at the given `index`.

        Args:
            index (QModelIndex): The model index, which points at a
                data object.
            role (Qt.ItemDataRole, optional): Defaults to `Qt.DisplayRole`. You
                have to use different roles to retrieve different data for an
                `index`. Accepted roles are `Qt.DisplayRole`, `Qt.EditRole` and
                `DTYPE_ROLE`.

        Returns:
            None if an invalid index is given, the role is not accepted by the
            model or the column is greater than `1`.
            The column name will be returned if the given column number equals `0`
            and the role is either `Qt.DisplayRole` or `Qt.EditRole`.
            The datatype will be returned, if the column number equals `1`. The
            `Qt.DisplayRole` or `Qt.EditRole` return a human readable, translated
            string, whereas the `DTYPE_ROLE` returns the raw data type.

        """

        # an index is invalid, if a row or column does not exist or extends
        # the bounds of self.columnCount() or self.rowCount()
        # therefor a check for col>1 is unnecessary.
        if not index.isValid():
            return None

        col = index.column()

        #row = self._dataFrame.columns[index.column()]
        columnName = self._dataFrame.columns[index.row()]
        columnDtype = self._dataFrame[columnName].dtype

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if col == 0:
                if columnName == index.row():
                    return index.row()
                return columnName
            elif col == 1:
                return SupportedDtypes.description(columnDtype)
        elif role == DTYPE_ROLE:
            if col == 1:
                return columnDtype
            else:
                return None

    def setData(self, index, value, role=DTYPE_CHANGE_ROLE):
        """Updates the datatype of a column.

        The model must be initated with a dataframe already, since valid
        indexes are necessary. The `value` is a translated description of the
        data type. The translations can be found at
        `qtpandas.translation.DTypeTranslator`.

        If a datatype can not be converted, e.g. datetime to integer, a
        `NotImplementedError` will be raised.

        Args:
            index (QModelIndex): The index of the column to be changed.
            value (str): The description of the new datatype, e.g.
                `positive kleine ganze Zahl (16 Bit)`.
            role (Qt.ItemDataRole, optional): The role, which accesses and
                changes data. Defaults to `DTYPE_CHANGE_ROLE`.

        Raises:
            NotImplementedError: If an error during conversion occured.

        Returns:
            bool: `True` if the datatype could be changed, `False` if not or if
                the new datatype equals the old one.

        """
        if role != DTYPE_CHANGE_ROLE or not index.isValid():
            return False

        if not self.editable():
            return False

        self.layoutAboutToBeChanged.emit()

        dtype = SupportedDtypes.dtype(value)
        currentDtype = np.dtype(index.data(role=DTYPE_ROLE))

        if dtype is not None:
            if dtype != currentDtype:
                # col = index.column()
                # row = self._dataFrame.columns[index.column()]
                columnName = self._dataFrame.columns[index.row()]

                try:
                    if dtype == np.dtype('<M8[ns]'):
                        if currentDtype in SupportedDtypes.boolTypes():
                            raise Exception("Can't convert a boolean value into a datetime value.")
                        self._dataFrame[columnName] = self._dataFrame[columnName].apply(pd.to_datetime)
                    else:
                        self._dataFrame[columnName] = self._dataFrame[columnName].astype(dtype)
                    self.dtypeChanged.emit(index.row(), dtype)
                    self.layoutChanged.emit()

                    return True
                except Exception:
                    message = 'Could not change datatype %s of column %s to datatype %s' % (currentDtype, columnName, dtype)
                    self.changeFailed.emit(message, index, dtype)
                    raise
                    # self._dataFrame[columnName] = self._dataFrame[columnName].astype(currentDtype)
                    # self.layoutChanged.emit()
                    # self.dtypeChanged.emit(columnName)
                    #raise NotImplementedError, "dtype changing not fully working, original error:\n{}".format(e)
        return False


    def flags(self, index):
        """Returns the item flags for the given index as ored value, e.x.: Qt.ItemIsUserCheckable | Qt.ItemIsEditable

        Args:
            index (QModelIndex): Index to define column and row

        Returns:
            for column 'column': Qt.ItemIsSelectable | Qt.ItemIsEnabled
            for column 'data type': Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

        """
        if not index.isValid():
            return Qt.NoItemFlags

        col = index.column()

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if col > 0 and self.editable():
            flags |= Qt.ItemIsEditable

        return flags

    def rowCount(self, index=QModelIndex()):
        """returns number of rows

        Args:
            index (QModelIndex, optional): Index to define column and row. defaults to empty QModelIndex

        Returns:
            number of rows
        """
        return len(self._dataFrame.columns)

    def columnCount(self, index=QModelIndex()):
        """returns number of columns

        Args:
            index (QModelIndex, optional): Index to define column and row. defaults to empty QModelIndex

        Returns:
            number of columns
        """
        return len(self.headers)


class DataFrameModel(QAbstractTableModel):
    """data model for use in QTableView, QListView, QComboBox, etc.

    Attributes:
        timestampFormat (unicode): formatting string for conversion of timestamps to QDateTime.
            Used in data method.
        sortingAboutToStart (Signal): emitted directly before sorting starts.
        sortingFinished (Signal): emitted, when sorting finished.
        dtypeChanged (Signal(columnName)): passed from related ColumnDtypeModel
            if a columns dtype has changed.
        changingDtypeFailed (Signal(columnName, index, dtype)):
            passed from related ColumnDtypeModel.
            emitted after a column has changed it's data type.
        dataChanged (Signal):
            Emitted, if data has changed, e.x. finished loading, new columns added or removed.
            It's not the same as layoutChanged.
            Usefull to reset delegates in the view.
    """

    _float_precisions = {
        "float16": np.finfo(np.float16).precision - 2,
        "float32": np.finfo(np.float32).precision - 1,
        "float64": np.finfo(np.float64).precision - 1
    }

    """list of int datatypes for easy checking in data() and setData()"""
    _intDtypes = SupportedDtypes.intTypes() + SupportedDtypes.uintTypes()
    """list of float datatypes for easy checking in data() and setData()"""
    _floatDtypes = SupportedDtypes.floatTypes()
    """list of bool datatypes for easy checking in data() and setData()"""
    _boolDtypes = SupportedDtypes.boolTypes()
    """list of datetime datatypes for easy checking in data() and setData()"""
    _dateDtypes = SupportedDtypes.datetimeTypes()

    _timestampFormat = Qt.ISODate

    sortingAboutToStart = Signal()
    sortingFinished = Signal()
    dtypeChanged = Signal(int, object)
    changingDtypeFailed = Signal(object, QModelIndex, object)
    dataChanged = Signal()
    dataFrameChanged = Signal()

    def __init__(self, dataFrame: Optional[pd.DataFrame] = None) -> None:
        """

        Args:
            dataFrame (pandas.core.frame.DataFrame, optional): initializes the model with given DataFrame.
                If none is given an empty DataFrame will be set. defaults to None.
        """
        super(DataFrameModel, self).__init__()

        self._dataFrame = pd.DataFrame()

        if dataFrame is not None:
            self.setDataFrame(dataFrame)
            self.enableEditing()

        self.dataChanged.emit()

        self._dataFrameOriginal = None

    def dataFrame(self):
        """
        getter function to _dataFrame. Holds all data.

        Note:
            It's not implemented with python properties to keep Qt conventions.
            Not sure why??
        """
        return self._dataFrame

    def setDataFrame(self, dataFrame, copyDataFrame=False):
        """
        Setter function to _dataFrame. Holds all data.

        Note:
            It's not implemented with python properties to keep Qt conventions.

        Raises:
            TypeError: if dataFrame is not of type pandas.core.frame.DataFrame.

        Args:
            dataFrame (pandas.core.frame.DataFrame): assign dataFrame
                to_dataFrame. Holds all the data displayed.
            copyDataFrame (bool, optional): create a copy of dataFrame or use
                it as is. defaults to False. If you use it as is, you can
                change it from outside otherwise you have to reset the dataFrame
                after external changes.

        """
        if not isinstance(dataFrame, pd.core.frame.DataFrame):
            raise TypeError("not of type pandas.DataFrame")

        self.layoutAboutToBeChanged.emit()
        self._dataFrame = dataFrame.copy()

        self._columnDtypeModel = ColumnDtypeModel(dataFrame)
        self._columnDtypeModel.dtypeChanged.connect(self.propagateDtypeChanges)
        self._columnDtypeModel.changeFailed.connect(
            lambda columnName, index, dtype: self.changingDtypeFailed.emit(columnName, index, dtype)
        )
        self.layoutChanged.emit()
        self.dataChanged.emit()
        self.dataFrameChanged.emit()

    @Slot(int, object)
    def propagateDtypeChanges(self, column, dtype):
        """
        Emits a dtypeChanged signal with the column and dtype.

        :param column: (str)
        :param dtype: ??
        :return: None
        """
        self.dtypeChanged.emit(column, dtype)

    @property
    def timestampFormat(self):
        """getter to _timestampFormat"""
        return self._timestampFormat

    @timestampFormat.setter
    def timestampFormat(self, timestampFormat):
        """
        Setter to _timestampFormat. Formatting string for conversion of timestamps to QDateTime

        Raises:
            AssertionError: if timestampFormat is not of type unicode.

        Args:
            timestampFormat (unicode): assign timestampFormat to _timestampFormat.
                Formatting string for conversion of timestamps to QDateTime. Used in data method.

        """
        if not isinstance(timestampFormat, str):
            raise TypeError('not of type unicode')
        #assert isinstance(timestampFormat, unicode) or timestampFormat.__class__.__name__ == "DateFormat", "not of type unicode"
        self._timestampFormat = timestampFormat

    def rename(self, index=None, columns=None, **kwargs):
        """
        Renames the dataframe inplace calling appropriate signals.
        Wraps pandas.DataFrame.rename(*args, **kwargs) - overrides
        the inplace kwarg setting it to True.

        Example use:
        renames = {'colname1':'COLNAME_1', 'colname2':'COL2'}
        DataFrameModel.rename(columns=renames)

        :param args:
            see pandas.DataFrame.rename
        :param kwargs:
            see pandas.DataFrame.rename
        :return:
            None
        """
        kwargs['inplace'] = True
        self.layoutAboutToBeChanged.emit()
        self._dataFrame.rename(index, columns, **kwargs)
        self.layoutChanged.emit()
        self.dataChanged.emit()
        self.dataFrameChanged.emit()

    def applyFunction(self, func):
        """
        Applies a function to the dataFrame with appropriate signals.
        The function must return a dataframe.
        :param func: A function (or partial function) that accepts a dataframe as the first argument.
        :return: None
        :raise:
            AssertionError if the func is not callable.
            AssertionError if the func does not return a DataFrame.
        """
        assert callable(func), "function {} is not callable".format(func)
        self.layoutAboutToBeChanged.emit()
        df = func(self._dataFrame)
        assert isinstance(df, pd.DataFrame), "function {} did not return a DataFrame.".format(func.__name__)
        self._dataFrame = df
        self.layoutChanged.emit()
        self.dataChanged.emit()
        self.dataFrameChanged.emit()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Return the header depending on section, orientation and Qt::ItemDataRole

        Args:
            section (int): For horizontal headers, the section number corresponds to the column number.
                Similarly, for vertical headers, the section number corresponds to the row number.
            orientation (Qt::Orientations):
            role (Qt::ItemDataRole):

        Returns:
            None if not Qt.DisplayRole
            _dataFrame.columns.tolist()[section] if orientation == Qt.Horizontal
            section if orientation == Qt.Vertical
            None if horizontal orientation and section raises IndexError
        """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            try:
                label = self._dataFrame.columns.tolist()[section]
                if label == section:
                    label = section
                return label
            except (IndexError, ):
                return None
        elif orientation == Qt.Vertical:
            return section

    def data(self, index, role=Qt.DisplayRole):
        """return data depending on index, Qt::ItemDataRole and data type of the column.

        Args:
            index (QModelIndex): Index to define column and row you want to return
            role (Qt::ItemDataRole): Define which data you want to return.

        Returns:
            None if index is invalid
            None if role is none of: DisplayRole, EditRole, CheckStateRole, DATAFRAME_ROLE

            if role DisplayRole:
                unmodified _dataFrame value if column dtype is object (string or unicode).
                _dataFrame value as int or long if column dtype is in _intDtypes.
                _dataFrame value as float if column dtype is in _floatDtypes. Rounds to defined precision (look at: _float16_precision, _float32_precision).
                None if column dtype is in _boolDtypes.
                QDateTime if column dtype is numpy.timestamp64[ns]. Uses timestampFormat as conversion template.

            if role EditRole:
                unmodified _dataFrame value if column dtype is object (string or unicode).
                _dataFrame value as int or long if column dtype is in _intDtypes.
                _dataFrame value as float if column dtype is in _floatDtypes. Rounds to defined precision (look at: _float16_precision, _float32_precision).
                _dataFrame value as bool if column dtype is in _boolDtypes.
                QDateTime if column dtype is numpy.timestamp64[ns]. Uses timestampFormat as conversion template.

            if role CheckStateRole:
                Qt.Checked or Qt.Unchecked if dtype is numpy.bool_ otherwise None for all other dtypes.

            if role DATAFRAME_ROLE:
                unmodified _dataFrame value.

            raises TypeError if an unhandled dtype is found in column.
        """

        if not index.isValid():
            return None

        def convertValue(row, col, columnDtype):
            value = None
            if columnDtype == object:
                value = self._dataFrame.ix[row, col]
            elif columnDtype in self._floatDtypes:
                value = round(float(self._dataFrame.ix[row, col]), self._float_precisions[str(columnDtype)])
            elif columnDtype in self._intDtypes:
                value = int(self._dataFrame.ix[row, col])
            elif columnDtype in self._boolDtypes:
                # TODO this will most likely always be true
                # See: http://stackoverflow.com/a/715455
                # well no: I am mistaken here, the data is already in the dataframe
                # so its already converted to a bool
                value = bool(self._dataFrame.ix[row, col])

            elif columnDtype in self._dateDtypes:
                #print numpy.datetime64(self._dataFrame.ix[row, col])
                value = pd.Timestamp(self._dataFrame.ix[row, col])
                value = QDateTime.fromString(str(value), self.timestampFormat)
                #print value
            # else:
            #     raise TypeError, "returning unhandled data type"
            return value

        row = self._dataFrame.index[index.row()]
        col = self._dataFrame.columns[index.column()]
        columnDtype = self._dataFrame[col].dtype

        if role == Qt.DisplayRole:
            # return the value if you wanne show True/False as text
            if columnDtype == np.bool:
                result = self._dataFrame.ix[row, col]
            else:
                result = convertValue(row, col, columnDtype)
        elif role == Qt.EditRole:
            result = convertValue(row, col, columnDtype)
        elif role == Qt.CheckStateRole:
            if columnDtype == np.bool_:
                if convertValue(row, col, columnDtype):
                    result = Qt.Checked
                else:
                    result = Qt.Unchecked
            else:
                result = None
        elif role == DATAFRAME_ROLE:
            result = self._dataFrame.ix[row, col]
        else:
            result = None
        return result

    def flags(self, index):
        """Returns the item flags for the given index as ored value, e.x.: Qt.ItemIsUserCheckable | Qt.ItemIsEditable

        If a combobox for bool values should pop up ItemIsEditable have to set for bool columns too.

        Args:
            index (QModelIndex): Index to define column and row

        Returns:
            if column dtype is not boolean Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
            if column dtype is boolean Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        """
        flags = super(DataFrameModel, self).flags(index)

        if not self.editable:
            return flags

        col = self._dataFrame.columns[index.column()]
        if self._dataFrame[col].dtype == np.bool:
            flags |= Qt.ItemIsUserCheckable
        else:
            # if you want to have a combobox for bool columns set this
            flags |= Qt.ItemIsEditable

        return flags

    def setData(self, index, value, role=Qt.DisplayRole):
        """Set the value to the index position depending on Qt::ItemDataRole and data type of the column

        Args:
            index (QModelIndex): Index to define column and row.
            value (object): new value.
            role (Qt::ItemDataRole): Use this role to specify what you want to do.

        Raises:
            TypeError: If the value could not be converted to a known datatype.

        Returns:
            True if value is changed. Calls layoutChanged after update.
            False if value is not different from original value.

        """
        if not index.isValid() or not self.editable:
            return False

        if value != index.data(role):

            self.layoutAboutToBeChanged.emit()

            row = self._dataFrame.index[index.row()]
            col = self._dataFrame.columns[index.column()]
            #print 'before change: ', index.data().toUTC(), self._dataFrame.iloc[row][col]
            columnDtype = self._dataFrame[col].dtype

            if columnDtype == object:
                pass

            elif columnDtype in self._intDtypes:
                dtypeInfo = np.iinfo(columnDtype)
                if value < dtypeInfo.min:
                    value = dtypeInfo.min
                elif value > dtypeInfo.max:
                    value = dtypeInfo.max

            elif columnDtype in self._floatDtypes:
                value = np.float64(value).astype(columnDtype)

            elif columnDtype in self._boolDtypes:
                value = np.bool_(value)

            elif columnDtype in self._dateDtypes:
                # convert the given value to a compatible datetime object.
                # if the conversation could not be done, keep the original
                # value.
                if isinstance(value, QDateTime):
                    value = value.toString(self.timestampFormat)
                try:
                    value = pd.Timestamp(value)
                except Exception:
                    raise Exception("Can't convert '{0}' into a datetime".format(value))
                    # return False
            else:
                raise TypeError("try to set unhandled data type")

            self._dataFrame.at[row, col] = value

            #print 'after change: ', value, self._dataFrame.iloc[row][col]
            self.layoutChanged.emit()
            return True
        else:
            return False

    def rowCount(self, index=QModelIndex()):
        """returns number of rows

        Args:
            index (QModelIndex, optional): Index to define column and row. defaults to empty QModelIndex

        Returns:
            number of rows
        """
        # len(df.index) is faster, so use it:
        # In [12]: %timeit df.shape[0]
        # 1000000 loops, best of 3: 437 ns per loop
        # In [13]: %timeit len(df.index)
        # 10000000 loops, best of 3: 110 ns per loop
        # %timeit df.__len__()
        # 1000000 loops, best of 3: 215 ns per loop
        return len(self._dataFrame.index)

    def columnCount(self, index=QModelIndex()):
        """returns number of columns

        Args:
            index (QModelIndex, optional): Index to define column and row. defaults to empty QModelIndex

        Returns:
            number of columns
        """
        # speed comparison:
        # In [23]: %timeit len(df.columns)
        # 10000000 loops, best of 3: 108 ns per loop

        # In [24]: %timeit df.shape[1]
        # 1000000 loops, best of 3: 440 ns per loop
        return len(self._dataFrame.columns)

    def sort(self, columnId, order=Qt.AscendingOrder):
        """
        Sorts the model column

        After sorting the data in ascending or descending order, a signal
        `layoutChanged` is emitted.

        :param: columnId (int)
            the index of the column to sort on.
        :param: order (Qt::SortOrder, optional)
            descending(1) or ascending(0). defaults to Qt.AscendingOrder

        """
        self.layoutAboutToBeChanged.emit()
        self.sortingAboutToStart.emit()
        column = self._dataFrame.columns[columnId]
        self._dataFrame.sort_values(column, ascending=not bool(order), inplace=True)
        self.layoutChanged.emit()
        self.sortingFinished.emit()

    def columnDtypeModel(self):
        """
        Getter for a ColumnDtypeModel.

        :return:
            qtpandas.models.ColumnDtypeModel
        """
        return self._columnDtypeModel


    def enableEditing(self, editable=True):
        """
        Sets the DataFrameModel and columnDtypeModel's
        editable properties.
        :param editable: bool
            defaults to True,
            False disables most editing methods.
        :return:
            None
        """
        self.editable = editable
        self._columnDtypeModel.setEditable(self.editable)

    def dataFrameColumns(self):
        """
        :return: list containing dataframe columns
        """
        return self._dataFrame.columns.tolist()

    def addDataFrameColumn(self, columnName, dtype=str, defaultValue=None):
        """
        Adds a column to the dataframe as long as
        the model's editable property is set to True and the
        dtype is supported.

        :param columnName: str
            name of the column.
        :param dtype: qtpandas.models.SupportedDtypes option
        :param defaultValue: (object)
            to default the column's value to, should be the same as the dtype or None
        :return: (bool)
            True on success, False otherwise.
        """
        if not self.editable or dtype not in SupportedDtypes.allTypes():
            return False

        elements = self.rowCount()
        columnPosition = self.columnCount()

        newColumn = pd.Series([defaultValue]*elements, index=self._dataFrame.index, dtype=dtype)

        self.beginInsertColumns(QModelIndex(), columnPosition - 1, columnPosition - 1)
        try:
            self._dataFrame.insert(columnPosition, columnName, newColumn, allow_duplicates=False)
        except ValueError as e:
            # columnName does already exist
            return False

        self.endInsertColumns()

        self.propagateDtypeChanges(columnPosition, newColumn.dtype)

        return True

    def addDataFrameRows(self, count=1):
        """

        Adds rows to the dataframe.

        :param count: (int)
            The number of rows to add to the dataframe.
        :return: (bool)
            True on success, False on failure.

        """
        # don't allow any gaps in the data rows.
        # and always append at the end

        if not self.editable:
            return False

        position = self.rowCount()

        if count < 1:
            return False

        if len(self.dataFrame().columns) == 0:
            # log an error message or warning
            return False

        # Note: This function emits the rowsAboutToBeInserted() signal which
        # connected views (or proxies) must handle before the data is
        # inserted. Otherwise, the views may end up in an invalid state.
        self.beginInsertRows(QModelIndex(), position, position + count - 1)

        defaultValues = []
        for dtype in self._dataFrame.dtypes:
            if dtype.type == np.dtype('<M8[ns]'):
                val = pd.Timestamp('')
            elif dtype.type == np.dtype(object):
                val = ''
            else:
                val = dtype.type()
            defaultValues.append(val)

        # for i in range(count):
        #     self._dataFrame.loc[position + i] = defaultValues
        to_append = pd.DataFrame(index=range(position, position + count),
                                 columns=self._dataFrame.columns,
                                 data=[defaultValues])
        self._dataFrame = self._dataFrame.append(to_append)
        # self._dataFrame.loc[position:position + count] = defaultValues
        self._dataFrame.reset_index(inplace=True, drop=True)
        self.endInsertRows()
        return True

    def removeDataFrameColumns(self, columns):
        """
        Removes columns from the dataframe.
        :param columns: [(int, str)]
        :return: (bool)
            True on success, False on failure.
        """
        if not self.editable:
            return False

        if columns:
            deleted = 0
            errored = False
            for (position, name) in columns:
                position = position - deleted
                if position < 0:
                    position = 0
                self.beginRemoveColumns(QModelIndex(), position, position)
                try:
                    self._dataFrame.drop(name, axis=1, inplace=True)
                except ValueError as e:
                    errored = True
                    continue
                self.endRemoveColumns()
                deleted += 1
            self.dataChanged.emit()

            if errored:
                return False
            else:
                return True
        return False

    def removeDataFrameRows(self, rows):
        """
        Removes rows from the dataframe.

        :param rows: (list)
            of row indexes to remove.
        :return: (bool)
            True on success, False on failure.
        """
        if not self.editable:
            return False

        if len(rows) > 0:
            position = min(rows)
            count = len(rows)
            self.beginRemoveRows(QModelIndex(), position, position + count - 1)

            removedAny = False
            for idx, line in self._dataFrame.iterrows():
                if idx in rows:
                    removedAny = True
                    self._dataFrame.drop(idx, inplace=True)

            if not removedAny:
                return False

            self._dataFrame.reset_index(inplace=True, drop=True)

            self.endRemoveRows()
            return True
        return False

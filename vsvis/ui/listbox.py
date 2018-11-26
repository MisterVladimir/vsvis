# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'listbox.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from qtpy import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 299)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupbox = QtWidgets.QGroupBox(Form)
        self.groupbox.setObjectName("groupbox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupbox)
        self.gridLayout.setObjectName("gridLayout")
        self.clear_button = QtWidgets.QPushButton(self.groupbox)
        self.clear_button.setObjectName("clear_button")
        self.gridLayout.addWidget(self.clear_button, 1, 2, 1, 1)
        self.sort_button = QtWidgets.QPushButton(self.groupbox)
        self.sort_button.setObjectName("sort_button")
        self.gridLayout.addWidget(self.sort_button, 1, 0, 1, 1)
        self.list_view = QtWidgets.QListView(self.groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_view.sizePolicy().hasHeightForWidth())
        self.list_view.setSizePolicy(sizePolicy)
        self.list_view.setAcceptDrops(True)
        self.list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.list_view.setDragEnabled(False)
        self.list_view.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.list_view.setObjectName("list_view")
        self.gridLayout.addWidget(self.list_view, 0, 0, 1, 3)
        self.delete_button = QtWidgets.QPushButton(self.groupbox)
        self.delete_button.setObjectName("delete_button")
        self.gridLayout.addWidget(self.delete_button, 1, 1, 1, 1)
        self.horizontalLayout.addWidget(self.groupbox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupbox.setTitle(_translate("Form", "Images"))
        self.clear_button.setText(_translate("Form", "Clear"))
        self.sort_button.setText(_translate("Form", "Sort"))
        self.list_view.setToolTip(_translate("Form", "Drop image data here"))
        self.delete_button.setText(_translate("Form", "Delete"))


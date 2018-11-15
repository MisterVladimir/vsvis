# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'file_inspection_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_file_inspection_dialog(object):
    def setupUi(self, file_inspection_dialog):
        file_inspection_dialog.setObjectName("file_inspection_dialog")
        file_inspection_dialog.resize(731, 554)
        self.verticalLayout = QtWidgets.QVBoxLayout(file_inspection_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_widget = QtWidgets.QWidget(file_inspection_dialog)
        self.main_widget.setObjectName("main_widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.main_widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.file_structure_groupbox = QtWidgets.QGroupBox(self.main_widget)
        self.file_structure_groupbox.setObjectName("file_structure_groupbox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.file_structure_groupbox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.file_structure_tree_view = QtWidgets.QTreeView(self.file_structure_groupbox)
        self.file_structure_tree_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.file_structure_tree_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.file_structure_tree_view.setObjectName("file_structure_tree_view")
        self.verticalLayout_3.addWidget(self.file_structure_tree_view)
        self.horizontalLayout.addWidget(self.file_structure_groupbox)
        self.data_info_groupbox = QtWidgets.QGroupBox(self.main_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.data_info_groupbox.sizePolicy().hasHeightForWidth())
        self.data_info_groupbox.setSizePolicy(sizePolicy)
        self.data_info_groupbox.setObjectName("data_info_groupbox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.data_info_groupbox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.data_info_table_view = QtWidgets.QTableView(self.data_info_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.data_info_table_view.sizePolicy().hasHeightForWidth())
        self.data_info_table_view.setSizePolicy(sizePolicy)
        self.data_info_table_view.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.data_info_table_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.data_info_table_view.setTabKeyNavigation(False)
        self.data_info_table_view.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.data_info_table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.data_info_table_view.setShowGrid(True)
        self.data_info_table_view.setGridStyle(QtCore.Qt.DotLine)
        self.data_info_table_view.setObjectName("data_info_table_view")
        self.data_info_table_view.horizontalHeader().setDefaultSectionSize(60)
        self.data_info_table_view.horizontalHeader().setMinimumSectionSize(25)
        self.verticalLayout_2.addWidget(self.data_info_table_view)
        self.horizontalLayout.addWidget(self.data_info_groupbox)
        self.verticalLayout.addWidget(self.main_widget)
        self.button_box = QtWidgets.QDialogButtonBox(file_inspection_dialog)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")
        self.verticalLayout.addWidget(self.button_box)

        self.retranslateUi(file_inspection_dialog)
        self.button_box.accepted.connect(file_inspection_dialog.accept)
        self.button_box.rejected.connect(file_inspection_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(file_inspection_dialog)

    def retranslateUi(self, file_inspection_dialog):
        _translate = QtCore.QCoreApplication.translate
        file_inspection_dialog.setWindowTitle(_translate("file_inspection_dialog", "Dialog"))
        self.file_structure_groupbox.setTitle(_translate("file_inspection_dialog", "File Structure"))
        self.data_info_groupbox.setTitle(_translate("file_inspection_dialog", "Data Info"))


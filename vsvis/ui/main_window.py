# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_main_window(object):
    def setupUi(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(897, 664)
        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.central_widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.graphics_widget = QtWidgets.QWidget(self.central_widget)
        self.graphics_widget.setObjectName("graphics_widget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.graphics_widget)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setSpacing(2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.resize_button = QtWidgets.QPushButton(self.graphics_widget)
        self.resize_button.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.resize_button.sizePolicy().hasHeightForWidth())
        self.resize_button.setSizePolicy(sizePolicy)
        self.resize_button.setMinimumSize(QtCore.QSize(34, 34))
        self.resize_button.setMaximumSize(QtCore.QSize(32, 34))
        self.resize_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/resize_medium"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.resize_button.setIcon(icon)
        self.resize_button.setIconSize(QtCore.QSize(32, 32))
        self.resize_button.setAutoDefault(False)
        self.resize_button.setDefault(False)
        self.resize_button.setFlat(False)
        self.resize_button.setObjectName("resize_button")
        self.horizontalLayout_5.addWidget(self.resize_button)
        self.zoom_out_button = QtWidgets.QPushButton(self.graphics_widget)
        self.zoom_out_button.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.zoom_out_button.sizePolicy().hasHeightForWidth())
        self.zoom_out_button.setSizePolicy(sizePolicy)
        self.zoom_out_button.setMinimumSize(QtCore.QSize(34, 34))
        self.zoom_out_button.setMaximumSize(QtCore.QSize(40, 34))
        self.zoom_out_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/zoom_in_small"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.zoom_out_button.setIcon(icon1)
        self.zoom_out_button.setIconSize(QtCore.QSize(24, 24))
        self.zoom_out_button.setObjectName("zoom_out_button")
        self.horizontalLayout_5.addWidget(self.zoom_out_button)
        self.zoom_in_button = QtWidgets.QPushButton(self.graphics_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.zoom_in_button.sizePolicy().hasHeightForWidth())
        self.zoom_in_button.setSizePolicy(sizePolicy)
        self.zoom_in_button.setMinimumSize(QtCore.QSize(40, 34))
        self.zoom_in_button.setMaximumSize(QtCore.QSize(40, 34))
        self.zoom_in_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/zoom_out_small"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.zoom_in_button.setIcon(icon2)
        self.zoom_in_button.setIconSize(QtCore.QSize(24, 24))
        self.zoom_in_button.setObjectName("zoom_in_button")
        self.horizontalLayout_5.addWidget(self.zoom_in_button)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.verticalLayout_4.addLayout(self.horizontalLayout_5)
        self.view_layout = QtWidgets.QHBoxLayout()
        self.view_layout.setObjectName("view_layout")
        self.graphics_view = VGraphicsView(self.graphics_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphics_view.sizePolicy().hasHeightForWidth())
        self.graphics_view.setSizePolicy(sizePolicy)
        self.graphics_view.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.graphics_view.setFrameShadow(QtWidgets.QFrame.Plain)
        self.graphics_view.setLineWidth(1)
        self.graphics_view.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.graphics_view.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.graphics_view.setObjectName("graphics_view")
        self.view_layout.addWidget(self.graphics_view)
        self.graphics_view_scrollbar = QtWidgets.QScrollBar(self.graphics_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphics_view_scrollbar.sizePolicy().hasHeightForWidth())
        self.graphics_view_scrollbar.setSizePolicy(sizePolicy)
        self.graphics_view_scrollbar.setMinimumSize(QtCore.QSize(0, 0))
        self.graphics_view_scrollbar.setOrientation(QtCore.Qt.Vertical)
        self.graphics_view_scrollbar.setInvertedAppearance(False)
        self.graphics_view_scrollbar.setObjectName("graphics_view_scrollbar")
        self.view_layout.addWidget(self.graphics_view_scrollbar)
        self.verticalLayout_4.addLayout(self.view_layout)
        self.horizontalLayout.addWidget(self.graphics_widget)
        self.control_panel_widget = QtWidgets.QWidget(self.central_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.control_panel_widget.sizePolicy().hasHeightForWidth())
        self.control_panel_widget.setSizePolicy(sizePolicy)
        self.control_panel_widget.setObjectName("control_panel_widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.control_panel_widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.data_display_groupbox = QtWidgets.QGroupBox(self.control_panel_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.data_display_groupbox.sizePolicy().hasHeightForWidth())
        self.data_display_groupbox.setSizePolicy(sizePolicy)
        self.data_display_groupbox.setFlat(False)
        self.data_display_groupbox.setObjectName("data_display_groupbox")
        self.gridLayout = QtWidgets.QGridLayout(self.data_display_groupbox)
        self.gridLayout.setObjectName("gridLayout")
        self.predicted_combobox = QtWidgets.QComboBox(self.data_display_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.predicted_combobox.sizePolicy().hasHeightForWidth())
        self.predicted_combobox.setSizePolicy(sizePolicy)
        self.predicted_combobox.setObjectName("predicted_combobox")
        self.gridLayout.addWidget(self.predicted_combobox, 1, 1, 1, 1)
        self.predicted_checkbox = QtWidgets.QCheckBox(self.data_display_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.predicted_checkbox.sizePolicy().hasHeightForWidth())
        self.predicted_checkbox.setSizePolicy(sizePolicy)
        self.predicted_checkbox.setObjectName("predicted_checkbox")
        self.gridLayout.addWidget(self.predicted_checkbox, 1, 0, 1, 1)
        self.ground_truth_combobox = QtWidgets.QComboBox(self.data_display_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ground_truth_combobox.sizePolicy().hasHeightForWidth())
        self.ground_truth_combobox.setSizePolicy(sizePolicy)
        self.ground_truth_combobox.setObjectName("ground_truth_combobox")
        self.gridLayout.addWidget(self.ground_truth_combobox, 0, 1, 1, 1)
        self.ground_truth_checkbox = QtWidgets.QCheckBox(self.data_display_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ground_truth_checkbox.sizePolicy().hasHeightForWidth())
        self.ground_truth_checkbox.setSizePolicy(sizePolicy)
        self.ground_truth_checkbox.setObjectName("ground_truth_checkbox")
        self.gridLayout.addWidget(self.ground_truth_checkbox, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.data_display_groupbox)
        self.table_tab_widget = QtWidgets.QTabWidget(self.control_panel_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.table_tab_widget.sizePolicy().hasHeightForWidth())
        self.table_tab_widget.setSizePolicy(sizePolicy)
        self.table_tab_widget.setObjectName("table_tab_widget")
        self.ground_truth_tab = QtWidgets.QWidget()
        self.ground_truth_tab.setObjectName("ground_truth_tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.ground_truth_tab)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.ground_truth_table_view = QtWidgets.QTableView(self.ground_truth_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ground_truth_table_view.sizePolicy().hasHeightForWidth())
        self.ground_truth_table_view.setSizePolicy(sizePolicy)
        self.ground_truth_table_view.setMouseTracking(True)
        self.ground_truth_table_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ground_truth_table_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ground_truth_table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ground_truth_table_view.setObjectName("ground_truth_table_view")
        self.ground_truth_table_view.horizontalHeader().setCascadingSectionResizes(False)
        self.verticalLayout_2.addWidget(self.ground_truth_table_view)
        self.table_tab_widget.addTab(self.ground_truth_tab, "")
        self.predicted_tab = QtWidgets.QWidget()
        self.predicted_tab.setObjectName("predicted_tab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.predicted_tab)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.predicted_table_view = QtWidgets.QTableView(self.predicted_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.predicted_table_view.sizePolicy().hasHeightForWidth())
        self.predicted_table_view.setSizePolicy(sizePolicy)
        self.predicted_table_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.predicted_table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.predicted_table_view.setObjectName("predicted_table_view")
        self.verticalLayout_3.addWidget(self.predicted_table_view)
        self.table_tab_widget.addTab(self.predicted_tab, "")
        self.verticalLayout.addWidget(self.table_tab_widget)
        self.probability_slider = VProbabilitySlider(self.control_panel_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.probability_slider.sizePolicy().hasHeightForWidth())
        self.probability_slider.setSizePolicy(sizePolicy)
        self.probability_slider.setAutoFillBackground(False)
        self.probability_slider.setMaximum(100)
        self.probability_slider.setSliderPosition(50)
        self.probability_slider.setOrientation(QtCore.Qt.Horizontal)
        self.probability_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.probability_slider.setObjectName("probability_slider")
        self.verticalLayout.addWidget(self.probability_slider)
        self.horizontalLayout.addWidget(self.control_panel_widget)
        main_window.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 897, 27))
        self.menubar.setObjectName("menubar")
        self.menu_file = QtWidgets.QMenu(self.menubar)
        self.menu_file.setObjectName("menu_file")
        self.menu_open_data = QtWidgets.QMenu(self.menu_file)
        self.menu_open_data.setObjectName("menu_open_data")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setSizeGripEnabled(True)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)
        self.action_open_image = QtWidgets.QAction(main_window)
        self.action_open_image.setObjectName("action_open_image")
        self.action_ground_truth = QtWidgets.QAction(main_window)
        self.action_ground_truth.setObjectName("action_ground_truth")
        self.action_predicted = QtWidgets.QAction(main_window)
        self.action_predicted.setObjectName("action_predicted")
        self.action_save = QtWidgets.QAction(main_window)
        self.action_save.setObjectName("action_save")
        self.action_save_as = QtWidgets.QAction(main_window)
        self.action_save_as.setObjectName("action_save_as")
        self.action_quit = QtWidgets.QAction(main_window)
        self.action_quit.setObjectName("action_quit")
        self.menu_open_data.addAction(self.action_ground_truth)
        self.menu_open_data.addAction(self.action_predicted)
        self.menu_file.addAction(self.menu_open_data.menuAction())
        self.menu_file.addAction(self.action_open_image)
        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_save_as)
        self.menu_file.addAction(self.action_quit)
        self.menubar.addAction(self.menu_file.menuAction())

        self.retranslateUi(main_window)
        self.table_tab_widget.setCurrentIndex(0)
        self.resize_button.clicked.connect(self.graphics_view.fit_to_window)
        self.zoom_in_button.clicked.connect(self.graphics_view.zoom_in)
        self.zoom_out_button.clicked.connect(self.graphics_view.zoom_out)
        self.table_tab_widget.currentChanged['int'].connect(self.probability_slider.activate)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "MainWindow"))
        self.zoom_out_button.setShortcut(_translate("main_window", "Ctrl+Shift+_"))
        self.zoom_in_button.setShortcut(_translate("main_window", "Ctrl++"))
        self.graphics_view_scrollbar.setToolTip(_translate("main_window", "Scroll through images"))
        self.data_display_groupbox.setTitle(_translate("main_window", "Displayed Data"))
        self.predicted_combobox.setToolTip(_translate("main_window", "Select predicted marker"))
        self.predicted_checkbox.setToolTip(_translate("main_window", "Show predicted data"))
        self.predicted_checkbox.setText(_translate("main_window", "Predicted"))
        self.ground_truth_combobox.setToolTip(_translate("main_window", "Select ground truth marker"))
        self.ground_truth_checkbox.setToolTip(_translate("main_window", "Show ground truth data"))
        self.ground_truth_checkbox.setText(_translate("main_window", "Ground Truth"))
        self.table_tab_widget.setTabText(self.table_tab_widget.indexOf(self.ground_truth_tab), _translate("main_window", "Ground Truth"))
        self.table_tab_widget.setTabText(self.table_tab_widget.indexOf(self.predicted_tab), _translate("main_window", "Predicted"))
        self.probability_slider.setToolTip(_translate("main_window", "Set probability"))
        self.menu_file.setTitle(_translate("main_window", "File"))
        self.menu_open_data.setTitle(_translate("main_window", "Open data..."))
        self.action_open_image.setText(_translate("main_window", "Open image..."))
        self.action_ground_truth.setText(_translate("main_window", "Ground Truth"))
        self.action_predicted.setText(_translate("main_window", "Predicted"))
        self.action_save.setText(_translate("main_window", "Save"))
        self.action_save.setShortcut(_translate("main_window", "Ctrl+S"))
        self.action_save_as.setText(_translate("main_window", "Save As..."))
        self.action_quit.setText(_translate("main_window", "Quit"))
        self.action_quit.setShortcut(_translate("main_window", "Ctrl+Q"))

from vsvis.promoted import VGraphicsView, VProbabilitySlider
import resources_rc
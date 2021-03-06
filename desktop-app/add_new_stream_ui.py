# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_new_stream.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_addCameraDialog(object):
    def setupUi(self, addCameraDialog):
        addCameraDialog.setObjectName("addCameraDialog")
        addCameraDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        addCameraDialog.resize(350, 476)
        addCameraDialog.setMinimumSize(QtCore.QSize(350, 360))
        addCameraDialog.setMaximumSize(QtCore.QSize(350, 500))
        addCameraDialog.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: #333333;")
        addCameraDialog.setModal(False)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(addCameraDialog)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.streamOptionLabel = QtWidgets.QLabel(addCameraDialog)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.streamOptionLabel.setFont(font)
        self.streamOptionLabel.setObjectName("streamOptionLabel")
        self.verticalLayout_4.addWidget(self.streamOptionLabel)
        self.usbSourceRadioButton = QtWidgets.QRadioButton(addCameraDialog)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.usbSourceRadioButton.setFont(font)
        self.usbSourceRadioButton.setStyleSheet("QRadioButton {\n"
"    background-color: #333333;\n"
"    color: #ffffff;\n"
"    padding: 3px;\n"
"}\n"
"QRadioButton::indicator {\n"
"    background-color: #ffffff;\n"
"    color: #262626;\n"
"    border-radius: 5px;\n"
"}\n"
"QRadioButton::indicator:checked {\n"
"    background-color: rgb(115, 210, 22);\n"
"}")
        self.usbSourceRadioButton.setChecked(True)
        self.usbSourceRadioButton.setObjectName("usbSourceRadioButton")
        self.verticalLayout_4.addWidget(self.usbSourceRadioButton)
        self.urlSourceRadioButton = QtWidgets.QRadioButton(addCameraDialog)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.urlSourceRadioButton.setFont(font)
        self.urlSourceRadioButton.setStyleSheet("QRadioButton {\n"
"    background-color: #333333;\n"
"    color: #ffffff;\n"
"    padding: 3px;\n"
"}\n"
"QRadioButton::indicator {\n"
"    background-color: #ffffff;\n"
"    color: #262626;\n"
"    border-radius: 5px;\n"
"}\n"
"QRadioButton::indicator:checked {\n"
"    background-color: rgb(115, 210, 22);\n"
"}")
        self.urlSourceRadioButton.setObjectName("urlSourceRadioButton")
        self.verticalLayout_4.addWidget(self.urlSourceRadioButton)
        self.verticalLayout_5.addLayout(self.verticalLayout_4)
        self.line_2 = QtWidgets.QFrame(addCameraDialog)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_5.addWidget(self.line_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, -1, -1, 10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 5, -1, -1)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.selectCamerasLabel = QtWidgets.QLabel(addCameraDialog)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.selectCamerasLabel.setFont(font)
        self.selectCamerasLabel.setObjectName("selectCamerasLabel")
        self.horizontalLayout.addWidget(self.selectCamerasLabel)
        self.reloadCamerasButton = QtWidgets.QPushButton(addCameraDialog)
        self.reloadCamerasButton.setMinimumSize(QtCore.QSize(30, 30))
        self.reloadCamerasButton.setMaximumSize(QtCore.QSize(30, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.reloadCamerasButton.setFont(font)
        self.reloadCamerasButton.setStyleSheet("QPushButton {\n"
"    background-color: #262626;\n"
"    color: #ffffff;\n"
"    border: 1px solid #555555;\n"
"    padding: 3px;\n"
"}\n"
"QPushButton::pressed {\n"
"    background-color: #888888;\n"
"    color: #262626;\n"
"}")
        self.reloadCamerasButton.setObjectName("reloadCamerasButton")
        self.horizontalLayout.addWidget(self.reloadCamerasButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.camerasCombobox = QtWidgets.QComboBox(addCameraDialog)
        self.camerasCombobox.setMinimumSize(QtCore.QSize(0, 30))
        self.camerasCombobox.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.camerasCombobox.setFont(font)
        self.camerasCombobox.setStyleSheet("background-color: rgb(46, 52, 54);")
        self.camerasCombobox.setEditable(False)
        self.camerasCombobox.setCurrentText("")
        self.camerasCombobox.setFrame(True)
        self.camerasCombobox.setModelColumn(0)
        self.camerasCombobox.setObjectName("camerasCombobox")
        self.verticalLayout.addWidget(self.camerasCombobox)
        self.verticalLayout_5.addLayout(self.verticalLayout)
        self.line = QtWidgets.QFrame(addCameraDialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_5.addWidget(self.line)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, -1, -1, 10)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(addCameraDialog)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.urlAddressField = QtWidgets.QLineEdit(addCameraDialog)
        self.urlAddressField.setEnabled(False)
        self.urlAddressField.setMinimumSize(QtCore.QSize(0, 30))
        self.urlAddressField.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.urlAddressField.setFont(font)
        self.urlAddressField.setStyleSheet("background-color: #333333;\n"
"border: 1px solid #555555;\n"
"padding: 3px;\n"
"color: #ffffff;")
        self.urlAddressField.setObjectName("urlAddressField")
        self.horizontalLayout_2.addWidget(self.urlAddressField)
        self.chooseFileButton = QtWidgets.QPushButton(addCameraDialog)
        self.chooseFileButton.setEnabled(False)
        self.chooseFileButton.setMinimumSize(QtCore.QSize(0, 30))
        self.chooseFileButton.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.chooseFileButton.setFont(font)
        self.chooseFileButton.setStyleSheet("QPushButton {\n"
"    background-color: #262626;\n"
"    color: #ffffff;\n"
"    border: 1px solid #555555;\n"
"    padding: 3px;\n"
"}\n"
"QPushButton::pressed {\n"
"    background-color: #888888;\n"
"    color: #262626;\n"
"}")
        self.chooseFileButton.setAutoDefault(False)
        self.chooseFileButton.setObjectName("chooseFileButton")
        self.horizontalLayout_2.addWidget(self.chooseFileButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout_5.addLayout(self.verticalLayout_2)
        self.line_3 = QtWidgets.QFrame(addCameraDialog)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout_5.addWidget(self.line_3)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.streamNameLabel = QtWidgets.QLabel(addCameraDialog)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.streamNameLabel.setFont(font)
        self.streamNameLabel.setObjectName("streamNameLabel")
        self.verticalLayout_3.addWidget(self.streamNameLabel)
        self.streamNameField = QtWidgets.QLineEdit(addCameraDialog)
        self.streamNameField.setMinimumSize(QtCore.QSize(0, 30))
        self.streamNameField.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.streamNameField.setFont(font)
        self.streamNameField.setStyleSheet("background-color: #333333;\n"
"border: 1px solid #555555;\n"
"padding: 3px;\n"
"color: #ffffff;")
        self.streamNameField.setObjectName("streamNameField")
        self.verticalLayout_3.addWidget(self.streamNameField)
        self.verticalLayout_5.addLayout(self.verticalLayout_3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.cancelButton = QtWidgets.QPushButton(addCameraDialog)
        self.cancelButton.setMinimumSize(QtCore.QSize(0, 30))
        self.cancelButton.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.cancelButton.setFont(font)
        self.cancelButton.setStyleSheet("QPushButton {\n"
"    background-color: #262626;\n"
"    color: #ffffff;\n"
"    border: 1px solid #555555;\n"
"    padding: 3px;\n"
"}\n"
"QPushButton::pressed {\n"
"    background-color: #888888;\n"
"    color: #262626;\n"
"}")
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_3.addWidget(self.cancelButton)
        self.addStreamButton = QtWidgets.QPushButton(addCameraDialog)
        self.addStreamButton.setMinimumSize(QtCore.QSize(0, 30))
        self.addStreamButton.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.addStreamButton.setFont(font)
        self.addStreamButton.setStyleSheet("QPushButton {\n"
"    background-color: #262626;\n"
"    color: #ffffff;\n"
"    border: 1px solid #555555;\n"
"    padding: 3px;\n"
"}\n"
"QPushButton::pressed {\n"
"    background-color: #888888;\n"
"    color: #262626;\n"
"}")
        self.addStreamButton.setObjectName("addStreamButton")
        self.horizontalLayout_3.addWidget(self.addStreamButton)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)

        self.retranslateUi(addCameraDialog)
        self.camerasCombobox.setCurrentIndex(-1)
        self.cancelButton.clicked.connect(addCameraDialog.close)
        self.usbSourceRadioButton.toggled['bool'].connect(self.camerasCombobox.setEnabled)
        self.urlSourceRadioButton.toggled['bool'].connect(self.urlAddressField.setEnabled)
        self.usbSourceRadioButton.toggled['bool'].connect(self.reloadCamerasButton.setEnabled)
        self.usbSourceRadioButton.toggled['bool'].connect(self.selectCamerasLabel.setEnabled)
        self.urlSourceRadioButton.toggled['bool'].connect(self.streamOptionLabel.setEnabled)
        self.urlAddressField.textChanged['QString'].connect(self.streamNameField.setText)
        self.usbSourceRadioButton.toggled['bool'].connect(self.urlAddressField.clear)
        self.camerasCombobox.currentIndexChanged['QString'].connect(self.streamNameField.setText)
        self.urlSourceRadioButton.toggled['bool'].connect(self.streamNameField.clear)
        self.usbSourceRadioButton.toggled['bool'].connect(self.chooseFileButton.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(addCameraDialog)
        addCameraDialog.setTabOrder(self.usbSourceRadioButton, self.urlSourceRadioButton)
        addCameraDialog.setTabOrder(self.urlSourceRadioButton, self.camerasCombobox)
        addCameraDialog.setTabOrder(self.camerasCombobox, self.reloadCamerasButton)
        addCameraDialog.setTabOrder(self.reloadCamerasButton, self.urlAddressField)
        addCameraDialog.setTabOrder(self.urlAddressField, self.addStreamButton)
        addCameraDialog.setTabOrder(self.addStreamButton, self.cancelButton)

    def retranslateUi(self, addCameraDialog):
        _translate = QtCore.QCoreApplication.translate
        addCameraDialog.setWindowTitle(_translate("addCameraDialog", "Add New Stream"))
        self.streamOptionLabel.setText(_translate("addCameraDialog", "Select source of stream"))
        self.usbSourceRadioButton.setText(_translate("addCameraDialog", "&USB Source"))
        self.urlSourceRadioButton.setText(_translate("addCameraDialog", "URL/File Source"))
        self.selectCamerasLabel.setText(_translate("addCameraDialog", "Select USB Camera"))
        self.reloadCamerasButton.setToolTip(_translate("addCameraDialog", "Reload connected cameras"))
        self.reloadCamerasButton.setText(_translate("addCameraDialog", "R"))
        self.label_2.setText(_translate("addCameraDialog", "Enter URL or File path"))
        self.urlAddressField.setPlaceholderText(_translate("addCameraDialog", "Type/Paste here"))
        self.chooseFileButton.setText(_translate("addCameraDialog", "..."))
        self.streamNameLabel.setText(_translate("addCameraDialog", "Name of video stream"))
        self.streamNameField.setPlaceholderText(_translate("addCameraDialog", "Type name of stream here"))
        self.cancelButton.setText(_translate("addCameraDialog", "Cancel"))
        self.addStreamButton.setText(_translate("addCameraDialog", "Add Stream"))

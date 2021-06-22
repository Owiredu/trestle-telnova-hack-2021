# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'video_player.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_videoPlayerMainWindow(object):
    def setupUi(self, videoPlayerMainWindow):
        videoPlayerMainWindow.setObjectName("videoPlayerMainWindow")
        videoPlayerMainWindow.resize(642, 400)
        videoPlayerMainWindow.setMinimumSize(QtCore.QSize(0, 400))
        videoPlayerMainWindow.setFocusPolicy(QtCore.Qt.StrongFocus)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/alpha_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        videoPlayerMainWindow.setWindowIcon(icon)
        videoPlayerMainWindow.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(136, 138, 133);")
        self.centralwidget = QtWidgets.QWidget(videoPlayerMainWindow)
        self.centralwidget.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.videoFrame = QtWidgets.QFrame(self.centralwidget)
        self.videoFrame.setStyleSheet("")
        self.videoFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.videoFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.videoFrame.setObjectName("videoFrame")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.videoFrame)
        self.gridLayout_3.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setHorizontalSpacing(0)
        self.gridLayout_3.setVerticalSpacing(6)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.frame_2 = QtWidgets.QFrame(self.videoFrame)
        self.frame_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_2.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_3.addWidget(self.frame_2, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.videoFrame, 0, 0, 1, 1)
        self.controlsFrame = QtWidgets.QFrame(self.centralwidget)
        self.controlsFrame.setMinimumSize(QtCore.QSize(0, 40))
        self.controlsFrame.setMaximumSize(QtCore.QSize(16777215, 40))
        self.controlsFrame.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: #333333;")
        self.controlsFrame.setObjectName("controlsFrame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.controlsFrame)
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.saveButton = QtWidgets.QPushButton(self.controlsFrame)
        self.saveButton.setMinimumSize(QtCore.QSize(32, 30))
        self.saveButton.setMaximumSize(QtCore.QSize(32, 30))
        self.saveButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.saveButton.setStyleSheet("QPushButton {\n"
"    background-color: #262626;\n"
"    color: #ffffff;\n"
"    border: 1px solid #555555;\n"
"    padding: 3px;\n"
"}\n"
"QPushButton::pressed {\n"
"    background-color: #888888;\n"
"    color: #262626;\n"
"}")
        self.saveButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveButton.setIcon(icon1)
        self.saveButton.setIconSize(QtCore.QSize(20, 20))
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.playPauseButton = QtWidgets.QPushButton(self.controlsFrame)
        self.playPauseButton.setMinimumSize(QtCore.QSize(32, 30))
        self.playPauseButton.setMaximumSize(QtCore.QSize(32, 30))
        self.playPauseButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.playPauseButton.setStyleSheet("QPushButton {\n"
"    background-color: #262626;\n"
"    color: #ffffff;\n"
"    border: 1px solid #555555;\n"
"    padding: 3px;\n"
"}\n"
"QPushButton::pressed {\n"
"    background-color: #888888;\n"
"    color: #262626;\n"
"}")
        self.playPauseButton.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.playPauseButton.setIcon(icon2)
        self.playPauseButton.setIconSize(QtCore.QSize(20, 20))
        self.playPauseButton.setObjectName("playPauseButton")
        self.horizontalLayout.addWidget(self.playPauseButton)
        self.stopButton = QtWidgets.QPushButton(self.controlsFrame)
        self.stopButton.setMinimumSize(QtCore.QSize(32, 30))
        self.stopButton.setMaximumSize(QtCore.QSize(32, 30))
        self.stopButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.stopButton.setStyleSheet("QPushButton {\n"
"    background-color: #262626;\n"
"    color: #ffffff;\n"
"    border: 1px solid #555555;\n"
"    padding: 3px;\n"
"}\n"
"QPushButton::pressed {\n"
"    background-color: #888888;\n"
"    color: #262626;\n"
"}")
        self.stopButton.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("icons/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stopButton.setIcon(icon3)
        self.stopButton.setIconSize(QtCore.QSize(20, 20))
        self.stopButton.setObjectName("stopButton")
        self.horizontalLayout.addWidget(self.stopButton)
        self.repeatButton = QtWidgets.QPushButton(self.controlsFrame)
        self.repeatButton.setMinimumSize(QtCore.QSize(32, 30))
        self.repeatButton.setMaximumSize(QtCore.QSize(32, 30))
        self.repeatButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.repeatButton.setStyleSheet("QPushButton {\n"
"    background-color: #262626;\n"
"    color: #ffffff;\n"
"    border: 1px solid #555555;\n"
"    padding: 3px;\n"
"}\n"
"QPushButton::pressed {\n"
"    background-color: #888888;\n"
"    color: #262626;\n"
"}")
        self.repeatButton.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("icons/repeat_off.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.repeatButton.setIcon(icon4)
        self.repeatButton.setIconSize(QtCore.QSize(20, 20))
        self.repeatButton.setCheckable(True)
        self.repeatButton.setObjectName("repeatButton")
        self.horizontalLayout.addWidget(self.repeatButton)
        self.line = QtWidgets.QFrame(self.controlsFrame)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, 4, -1, -1)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.progressSlider = QtWidgets.QSlider(self.controlsFrame)
        self.progressSlider.setMinimumSize(QtCore.QSize(225, 0))
        self.progressSlider.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.progressSlider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.progressSlider.setStyleSheet("background-color:#333333;")
        self.progressSlider.setMaximum(1000)
        self.progressSlider.setPageStep(20)
        self.progressSlider.setOrientation(QtCore.Qt.Horizontal)
        self.progressSlider.setObjectName("progressSlider")
        self.verticalLayout.addWidget(self.progressSlider)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, 5)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.currentTimeLabel = QtWidgets.QLabel(self.controlsFrame)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.currentTimeLabel.setFont(font)
        self.currentTimeLabel.setObjectName("currentTimeLabel")
        self.horizontalLayout_2.addWidget(self.currentTimeLabel)
        self.totalDurationLabel = QtWidgets.QLabel(self.controlsFrame)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.totalDurationLabel.setFont(font)
        self.totalDurationLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.totalDurationLabel.setObjectName("totalDurationLabel")
        self.horizontalLayout_2.addWidget(self.totalDurationLabel)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.line_2 = QtWidgets.QFrame(self.controlsFrame)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout.addWidget(self.line_2)
        self.videoRateComboBox = QtWidgets.QComboBox(self.controlsFrame)
        self.videoRateComboBox.setMinimumSize(QtCore.QSize(0, 30))
        self.videoRateComboBox.setMaximumSize(QtCore.QSize(80, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.videoRateComboBox.setFont(font)
        self.videoRateComboBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.videoRateComboBox.setEditable(False)
        self.videoRateComboBox.setMaxCount(20)
        self.videoRateComboBox.setObjectName("videoRateComboBox")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.videoRateComboBox.addItem("")
        self.horizontalLayout.addWidget(self.videoRateComboBox)
        self.gridLayout.addWidget(self.controlsFrame, 1, 0, 1, 1)
        videoPlayerMainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(videoPlayerMainWindow)
        self.videoRateComboBox.setCurrentIndex(9)
        QtCore.QMetaObject.connectSlotsByName(videoPlayerMainWindow)

    def retranslateUi(self, videoPlayerMainWindow):
        _translate = QtCore.QCoreApplication.translate
        videoPlayerMainWindow.setWindowTitle(_translate("videoPlayerMainWindow", "Video Player"))
        self.saveButton.setToolTip(_translate("videoPlayerMainWindow", "Save (D)"))
        self.playPauseButton.setToolTip(_translate("videoPlayerMainWindow", "Play (SPACE BAR)"))
        self.stopButton.setToolTip(_translate("videoPlayerMainWindow", "Stop (S)"))
        self.repeatButton.setToolTip(_translate("videoPlayerMainWindow", "Repeat OFF (R)"))
        self.currentTimeLabel.setText(_translate("videoPlayerMainWindow", "00:00:00"))
        self.totalDurationLabel.setText(_translate("videoPlayerMainWindow", "00:00:00"))
        self.videoRateComboBox.setToolTip(_translate("videoPlayerMainWindow", "Rate"))
        self.videoRateComboBox.setCurrentText(_translate("videoPlayerMainWindow", "x 1.0"))
        self.videoRateComboBox.setItemText(0, _translate("videoPlayerMainWindow", "x 0.1"))
        self.videoRateComboBox.setItemText(1, _translate("videoPlayerMainWindow", "x 0.2"))
        self.videoRateComboBox.setItemText(2, _translate("videoPlayerMainWindow", "x 0.3"))
        self.videoRateComboBox.setItemText(3, _translate("videoPlayerMainWindow", "x 0.4"))
        self.videoRateComboBox.setItemText(4, _translate("videoPlayerMainWindow", "x 0.5"))
        self.videoRateComboBox.setItemText(5, _translate("videoPlayerMainWindow", "x 0.6"))
        self.videoRateComboBox.setItemText(6, _translate("videoPlayerMainWindow", "x 0.7"))
        self.videoRateComboBox.setItemText(7, _translate("videoPlayerMainWindow", "x 0.8"))
        self.videoRateComboBox.setItemText(8, _translate("videoPlayerMainWindow", "x 0.9"))
        self.videoRateComboBox.setItemText(9, _translate("videoPlayerMainWindow", "x 1.0"))
        self.videoRateComboBox.setItemText(10, _translate("videoPlayerMainWindow", "x 1.1"))
        self.videoRateComboBox.setItemText(11, _translate("videoPlayerMainWindow", "x 1.2"))
        self.videoRateComboBox.setItemText(12, _translate("videoPlayerMainWindow", "x 1.3"))
        self.videoRateComboBox.setItemText(13, _translate("videoPlayerMainWindow", "x 1.4"))
        self.videoRateComboBox.setItemText(14, _translate("videoPlayerMainWindow", "x 1.5"))
        self.videoRateComboBox.setItemText(15, _translate("videoPlayerMainWindow", "x 1.6"))
        self.videoRateComboBox.setItemText(16, _translate("videoPlayerMainWindow", "x 1.7"))
        self.videoRateComboBox.setItemText(17, _translate("videoPlayerMainWindow", "x 1.8"))
        self.videoRateComboBox.setItemText(18, _translate("videoPlayerMainWindow", "x 1.9"))
        self.videoRateComboBox.setItemText(19, _translate("videoPlayerMainWindow", "x 2.0"))


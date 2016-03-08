# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CameraVue.ui'
#
# Created: Thu Jan 29 14:28:15 2015
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(745, 726)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.matplotlibGadget = MatplotlibWidget(self.centralwidget)
        self.matplotlibGadget.setGeometry(QtCore.QRect(10, 50, 441, 331))
        self.matplotlibGadget.setObjectName(_fromUtf8("matplotlibGadget"))
        self.cameraSelectComboBox = QtGui.QComboBox(self.centralwidget)
        self.cameraSelectComboBox.setGeometry(QtCore.QRect(150, 10, 161, 22))
        self.cameraSelectComboBox.setObjectName(_fromUtf8("cameraSelectComboBox"))
        self.cameraSelectLabel = QtGui.QLabel(self.centralwidget)
        self.cameraSelectLabel.setGeometry(QtCore.QRect(40, 10, 101, 16))
        self.cameraSelectLabel.setObjectName(_fromUtf8("cameraSelectLabel"))
        self.cameraSelectButton = QtGui.QPushButton(self.centralwidget)
        self.cameraSelectButton.setGeometry(QtCore.QRect(320, 10, 75, 23))
        self.cameraSelectButton.setObjectName(_fromUtf8("cameraSelectButton"))
        self.exposureLabel = QtGui.QLabel(self.centralwidget)
        self.exposureLabel.setGeometry(QtCore.QRect(470, 60, 101, 16))
        self.exposureLabel.setObjectName(_fromUtf8("exposureLabel"))
        self.gainLabel = QtGui.QLabel(self.centralwidget)
        self.gainLabel.setGeometry(QtCore.QRect(540, 90, 31, 20))
        self.gainLabel.setObjectName(_fromUtf8("gainLabel"))
        self.exposureEdit = QtGui.QLineEdit(self.centralwidget)
        self.exposureEdit.setGeometry(QtCore.QRect(570, 60, 113, 20))
        self.exposureEdit.setObjectName(_fromUtf8("exposureEdit"))
        self.gainEdit = QtGui.QLineEdit(self.centralwidget)
        self.gainEdit.setGeometry(QtCore.QRect(570, 90, 113, 20))
        self.gainEdit.setObjectName(_fromUtf8("gainEdit"))
        self.ciceroTextLabel = QtGui.QLabel(self.centralwidget)
        self.ciceroTextLabel.setGeometry(QtCore.QRect(10, 400, 141, 16))
        self.ciceroTextLabel.setObjectName(_fromUtf8("ciceroTextLabel"))
        self.cameraInfoLabel = QtGui.QLabel(self.centralwidget)
        self.cameraInfoLabel.setGeometry(QtCore.QRect(430, 400, 141, 16))
        self.cameraInfoLabel.setObjectName(_fromUtf8("cameraInfoLabel"))
        self.cameraUpdateButton = QtGui.QPushButton(self.centralwidget)
        self.cameraUpdateButton.setGeometry(QtCore.QRect(600, 120, 75, 23))
        self.cameraUpdateButton.setObjectName(_fromUtf8("cameraUpdateButton"))
        self.ciceroStartButton = QtGui.QPushButton(self.centralwidget)
        self.ciceroStartButton.setGeometry(QtCore.QRect(600, 10, 131, 23))
        self.ciceroStartButton.setObjectName(_fromUtf8("ciceroStartButton"))
        self.cameraRestoreButton = QtGui.QPushButton(self.centralwidget)
        self.cameraRestoreButton.setGeometry(QtCore.QRect(510, 120, 75, 23))
        self.cameraRestoreButton.setObjectName(_fromUtf8("cameraRestoreButton"))
        self.takeSnapshotButton = QtGui.QPushButton(self.centralwidget)
        self.takeSnapshotButton.setGeometry(QtCore.QRect(490, 180, 91, 23))
        self.takeSnapshotButton.setObjectName(_fromUtf8("takeSnapshotButton"))
        self.previewButton = QtGui.QPushButton(self.centralwidget)
        self.previewButton.setGeometry(QtCore.QRect(560, 150, 75, 23))
        self.previewButton.setObjectName(_fromUtf8("previewButton"))
        self.cameraEnableButton = QtGui.QPushButton(self.centralwidget)
        self.cameraEnableButton.setGeometry(QtCore.QRect(410, 10, 101, 23))
        self.cameraEnableButton.setObjectName(_fromUtf8("cameraEnableButton"))
        self.saveSnapshotButton = QtGui.QPushButton(self.centralwidget)
        self.saveSnapshotButton.setGeometry(QtCore.QRect(600, 180, 91, 23))
        self.saveSnapshotButton.setObjectName(_fromUtf8("saveSnapshotButton"))
        self.InformationCamera = QtGui.QTextBrowser(self.centralwidget)
        self.InformationCamera.setGeometry(QtCore.QRect(430, 420, 301, 261))
        self.InformationCamera.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.InformationCamera.setObjectName(_fromUtf8("InformationCamera"))
        self.CiceroCommunication = QtGui.QTextBrowser(self.centralwidget)
        self.CiceroCommunication.setGeometry(QtCore.QRect(10, 420, 411, 261))
        self.CiceroCommunication.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.CiceroCommunication.setObjectName(_fromUtf8("CiceroCommunication"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 745, 21))
        self.menubar.setDefaultUp(False)
        self.menubar.setNativeMenuBar(True)
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Camera Controller", None))
        self.cameraSelectLabel.setText(_translate("MainWindow", "Available cameras :", None))
        self.cameraSelectButton.setText(_translate("MainWindow", "Select", None))
        self.exposureLabel.setText(_translate("MainWindow", "Exposure time (ms) :", None))
        self.gainLabel.setText(_translate("MainWindow", "Gain :", None))
        self.ciceroTextLabel.setText(_translate("MainWindow", "Communication with Cicero : ", None))
        self.cameraInfoLabel.setText(_translate("MainWindow", "Camera information :", None))
        self.cameraUpdateButton.setText(_translate("MainWindow", "Update", None))
        self.ciceroStartButton.setText(_translate("MainWindow", "Start Cicero Server", None))
        self.cameraRestoreButton.setText(_translate("MainWindow", "Restore", None))
        self.takeSnapshotButton.setText(_translate("MainWindow", "Take Snapshot", None))
        self.previewButton.setText(_translate("MainWindow", "Preview", None))
        self.cameraEnableButton.setText(_translate("MainWindow", "Enable all cameras", None))
        self.saveSnapshotButton.setText(_translate("MainWindow", "Save Snapshot", None))

from Matplotlibgadget import MatplotlibWidget

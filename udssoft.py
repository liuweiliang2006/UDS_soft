# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'udssoft.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1078, 786)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(20, 10, 1021, 101))
        self.groupBox.setObjectName("groupBox")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 30, 68, 15))
        self.label.setObjectName("label")
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(90, 21, 101, 31))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(220, 30, 68, 15))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(10, 60, 68, 15))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(220, 60, 68, 21))
        self.label_4.setObjectName("label_4")
        self.comboBox_2 = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_2.setGeometry(QtCore.QRect(290, 20, 101, 22))
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_3 = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_3.setGeometry(QtCore.QRect(90, 60, 101, 22))
        self.comboBox_3.setObjectName("comboBox_3")
        self.comboBox_3.addItem("")
        self.comboBox_4 = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_4.setGeometry(QtCore.QRect(290, 60, 101, 22))
        self.comboBox_4.setObjectName("comboBox_4")
        self.comboBox_4.addItem("")
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setGeometry(QtCore.QRect(710, 20, 93, 28))
        self.pushButton.setObjectName("pushButton")
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(440, 20, 91, 16))
        self.label_5.setObjectName("label_5")
        self.label_12 = QtWidgets.QLabel(self.groupBox)
        self.label_12.setGeometry(QtCore.QRect(440, 60, 91, 16))
        self.label_12.setObjectName("label_12")
        self.lineEdit_5 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_5.setGeometry(QtCore.QRect(530, 20, 113, 20))
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.lineEdit_6 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_6.setGeometry(QtCore.QRect(530, 60, 113, 20))
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_3.setGeometry(QtCore.QRect(710, 60, 93, 28))
        self.pushButton_3.setObjectName("pushButton_3")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(20, 100, 1021, 611))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_2.setGeometry(QtCore.QRect(770, 50, 231, 91))
        self.groupBox_2.setObjectName("groupBox_2")
        self.label_6 = QtWidgets.QLabel(self.groupBox_2)
        self.label_6.setGeometry(QtCore.QRect(10, 30, 101, 16))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.groupBox_2)
        self.label_7.setGeometry(QtCore.QRect(10, 60, 101, 16))
        self.label_7.setObjectName("label_7")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_2.setGeometry(QtCore.QRect(110, 30, 113, 20))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_3.setGeometry(QtCore.QRect(110, 60, 113, 20))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_3.setGeometry(QtCore.QRect(770, 150, 231, 71))
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_8 = QtWidgets.QLabel(self.groupBox_3)
        self.label_8.setGeometry(QtCore.QRect(30, 30, 71, 16))
        self.label_8.setObjectName("label_8")
        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_4.setGeometry(QtCore.QRect(110, 30, 113, 20))
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_4.setGeometry(QtCore.QRect(20, 30, 721, 191))
        self.groupBox_4.setObjectName("groupBox_4")
        self.label_9 = QtWidgets.QLabel(self.groupBox_4)
        self.label_9.setGeometry(QtCore.QRect(50, 33, 101, 20))
        self.label_9.setObjectName("label_9")
        self.comboBox_5 = QtWidgets.QComboBox(self.groupBox_4)
        self.comboBox_5.setGeometry(QtCore.QRect(160, 30, 371, 22))
        self.comboBox_5.setObjectName("comboBox_5")
        self.comboBox_5.addItem("")
        self.label_10 = QtWidgets.QLabel(self.groupBox_4)
        self.label_10.setGeometry(QtCore.QRect(30, 70, 121, 16))
        self.label_10.setObjectName("label_10")
        self.comboBox_6 = QtWidgets.QComboBox(self.groupBox_4)
        self.comboBox_6.setGeometry(QtCore.QRect(160, 70, 371, 22))
        self.comboBox_6.setObjectName("comboBox_6")
        self.comboBox_6.addItem("")
        self.label_11 = QtWidgets.QLabel(self.groupBox_4)
        self.label_11.setGeometry(QtCore.QRect(50, 110, 101, 16))
        self.label_11.setObjectName("label_11")
        self.comboBox_7 = QtWidgets.QComboBox(self.groupBox_4)
        self.comboBox_7.setGeometry(QtCore.QRect(160, 110, 371, 22))
        self.comboBox_7.setObjectName("comboBox_7")
        self.comboBox_7.addItem("")
        self.groupBox_5 = QtWidgets.QGroupBox(self.groupBox_4)
        self.groupBox_5.setGeometry(QtCore.QRect(560, 20, 151, 111))
        self.groupBox_5.setObjectName("groupBox_5")
        self.radioButton = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton.setGeometry(QtCore.QRect(20, 30, 102, 19))
        self.radioButton.setObjectName("radioButton")
        self.radioButton_2 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_2.setGeometry(QtCore.QRect(20, 70, 102, 19))
        self.radioButton_2.setObjectName("radioButton_2")
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox_4)
        self.pushButton_2.setGeometry(QtCore.QRect(580, 150, 93, 28))
        self.pushButton_2.setObjectName("pushButton_2")
        self.label_14 = QtWidgets.QLabel(self.groupBox_4)
        self.label_14.setGeometry(QtCore.QRect(80, 150, 71, 16))
        self.label_14.setObjectName("label_14")
        self.lineEdit_7 = QtWidgets.QLineEdit(self.groupBox_4)
        self.lineEdit_7.setGeometry(QtCore.QRect(160, 150, 271, 20))
        self.lineEdit_7.setObjectName("lineEdit_7")
        self.label_15 = QtWidgets.QLabel(self.groupBox_4)
        self.label_15.setGeometry(QtCore.QRect(440, 150, 101, 20))
        self.label_15.setObjectName("label_15")
        self.tableView = QtWidgets.QTableView(self.tab)
        self.tableView.setGeometry(QtCore.QRect(20, 261, 981, 301))
        self.tableView.setObjectName("tableView")
        self.label_13 = QtWidgets.QLabel(self.tab)
        self.label_13.setGeometry(QtCore.QRect(30, 240, 101, 16))
        self.label_13.setObjectName("label_13")
        self.pushButton_4 = QtWidgets.QPushButton(self.tab)
        self.pushButton_4.setGeometry(QtCore.QRect(880, 230, 93, 28))
        self.pushButton_4.setObjectName("pushButton_4")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1078, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "设备配置"))
        self.label.setText(_translate("MainWindow", "设备类型："))
        self.comboBox.setItemText(0, _translate("MainWindow", "USBCAN-II"))
        self.label_2.setText(_translate("MainWindow", "设备索引："))
        self.label_3.setText(_translate("MainWindow", "CAN通道："))
        self.label_4.setText(_translate("MainWindow", "波特率："))
        self.comboBox_2.setItemText(0, _translate("MainWindow", "0"))
        self.comboBox_3.setItemText(0, _translate("MainWindow", "1"))
        self.comboBox_4.setItemText(0, _translate("MainWindow", "500K"))
        self.pushButton.setText(_translate("MainWindow", "打开"))
        self.label_5.setText(_translate("MainWindow", "过滤验收码："))
        self.label_12.setText(_translate("MainWindow", "过滤屏蔽码："))
        self.pushButton_3.setText(_translate("MainWindow", "关闭"))
        self.groupBox_2.setTitle(_translate("MainWindow", "地址"))
        self.label_6.setText(_translate("MainWindow", "物理地址：0x"))
        self.label_7.setText(_translate("MainWindow", "功能地址：0x"))
        self.lineEdit_3.setText(_translate("MainWindow", "7DF"))
        self.groupBox_3.setTitle(_translate("MainWindow", "网络层参数"))
        self.label_8.setText(_translate("MainWindow", "STmin(ms)"))
        self.lineEdit_4.setText(_translate("MainWindow", "20"))
        self.groupBox_4.setTitle(_translate("MainWindow", "服务参数设置"))
        self.label_9.setText(_translate("MainWindow", "服务标识(SID)"))
        self.comboBox_5.setItemText(0, _translate("MainWindow", "0x10-DiagnosticSessionControl"))
        self.label_10.setText(_translate("MainWindow", "子服务标识(SSID)"))
        self.comboBox_6.setItemText(0, _translate("MainWindow", "0x01-默认会话"))
        self.label_11.setText(_translate("MainWindow", "数据标识(DID)"))
        self.comboBox_7.setItemText(0, _translate("MainWindow", "0xF190-VINDataIdentifier"))
        self.groupBox_5.setTitle(_translate("MainWindow", "寻址方式"))
        self.radioButton.setText(_translate("MainWindow", "物理寻址"))
        self.radioButton_2.setText(_translate("MainWindow", "功能寻址"))
        self.pushButton_2.setText(_translate("MainWindow", "发送"))
        self.label_14.setText(_translate("MainWindow", "写入数据"))
        self.lineEdit_7.setText(_translate("MainWindow", "VIN1234567"))
        self.label_15.setText(_translate("MainWindow", "注:ASCII/DCD"))
        self.label_13.setText(_translate("MainWindow", "交互数据信息："))
        self.pushButton_4.setText(_translate("MainWindow", "清除数据"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "服务测试"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "下载升级"))

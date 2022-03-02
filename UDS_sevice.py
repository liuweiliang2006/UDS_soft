import binascii
import datetime
import queue
import struct
import threading
import time
import logging

from ControlCAN import *
from udsoncan.client import Client
from udsoncan.exceptions import TimeoutException
import udsoncan
from udsoncan.connections import BaseConnection
from udsoncan import services, Response, MemoryLocation

import isotp
from isotp import CanMessage
from functools import partial

import sys
import PyQt5.QtWidgets as qw
import UDS_sevice
import PyQt5.QtCore as qc
import udssoft
import os

class myMainWindow(qw.QMainWindow,udssoft.Ui_MainWindow):
    def __init__(self):
        super().__init__()#继承父类的方式实例化子类
        self.setupUi(self)
        self.comboBox_SID.currentTextChanged.connect(self.comboBox_SID_cb)

        #初始化默认参数
        # self.comboBox_SID.setCurrentText("0x11 - EcuReset")
        # self.comboBox_SID.setCurrentText("0x10-DiagnosticSessionControl")

    def comboBox_SID_cb(self):
        content = self.comboBox_SID.currentText()
        print("combox's value is", content)
        if "NONE" in content:
            self.display_data()
            self.display_SSID()
            self.display_DID()

        if "0x10" in content:
            print("0x10")
            self.display_SSID()
            self.Hide_data()
            self.Hide_DID()
            self.comboBox_SSID.addItem("0x01-默认会话")
            self.comboBox_SSID.addItem("0x02-编程会话")
            self.comboBox_SSID.addItem("0x03-扩展会话")

        if "0x11" in content:
            print("0x11")
            self.display_SSID()
            self.Hide_data()
            self.Hide_DID()
            self.comboBox_SSID.addItem("0x01-硬件复位")
            self.comboBox_SSID.addItem("0x02-钥匙开关复位")
            self.comboBox_SSID.addItem("0x01-软件复位")
        if "0x14" in content:
            print("0x14")
            self.display_SSID()
            self.Hide_data()
            self.Hide_DID()
            self.comboBox_SSID.addItem("0x100000-动力组")
            self.comboBox_SSID.addItem("0x200000-信息娱乐组")
            self.comboBox_SSID.addItem("0x400000-底盘和ADAS组")
            self.comboBox_SSID.addItem("0x800000-车身组")
            self.comboBox_SSID.addItem("0xC00000-网络通信组")
            self.comboBox_SSID.addItem("0xFFFFFF-所有组")
        if "0x19" in content:
            print("0x19")
            self.display_SSID()
            self.Hide_data()
            self.Hide_DID()
            self.comboBox_SSID.addItem("0x01-报告DTC数目")
            self.comboBox_SSID.addItem("0x02-报告DTC")
            self.comboBox_SSID.addItem("0x04-DTCSnapshot记录")
            self.comboBox_SSID.addItem("0x06-DTC扩展数据记录")
            self.comboBox_SSID.addItem("0x0A-报告支持的DTC")
        if "0x22" in content:
            print("0x22")
            self.Hide_SSID()
            self.Hide_data()
            self.display_DID()
            self.add_comboBox_DID()
            # self.comboBox_SSID.setEditable(False)
        if "0x23" in content:
            print("0x23")
        if "0x27" in content:
            print("0x27")
            self.display_SSID()
            self.Hide_data()
            self.Hide_DID()
            self.comboBox_SSID.addItem("0x01-请求种子(level 1)")
            self.comboBox_SSID.addItem("0x02-发送密钥(level 1)")
            self.comboBox_SSID.addItem("0x03-请求种子(level 2)")
            self.comboBox_SSID.addItem("0x04-发送密钥(level 2)")
            self.comboBox_SSID.addItem("0x09-请求种子(level 3)")
            self.comboBox_SSID.addItem("0x0A-发送密钥(level 3)")
        if "0x28" in content:
            print("0x28")
            self.display_SSID()
            self.Hide_data()
            self.Hide_DID()
            self.comboBox_SSID.addItem("0x00-enableRxAndTx")
            self.comboBox_SSID.addItem("0x01-enableRxAndDisableTx")
            self.comboBox_SSID.addItem("0x02-disableRxAndEnableTx")
            self.comboBox_SSID.addItem("0x03-disableRxAndTx")

        if "0x2A" in content:
            print("0x2A")
        if "0x2C" in content:
            print("0x2C")
        if "0x2E" in content:
            print("0x2E")
            self.display_DID()
            self.display_data()
            self.Hide_SSID()
            self.add_comboBox_DID()

        if "0x2F" in content:
            print("0x2F")
        if "0x31" in content:
            print("0x31")
        if "0x34" in content:
            print("0x34")
        if "0x36" in content:
            print("0x36")
        if "0x37" in content:
            print("0x37")
        if "0x3D" in content:
            print("0x3D")
        if "0x3E" in content:
            print("0x3E")
            self.display()
            self.comboBox_SSID.setHidden(True)
            self.label_SSID.setHidden(True)

        if "0x85" in content:
            print("0x85")
            self.display_SSID()
            self.Hide_data()
            self.Hide_DID()
            self.comboBox_SSID.addItem("0x01-ON 恢复诊断故障码设置")
            self.comboBox_SSID.addItem("0x02-OFF 停止诊断故障码设置")

    def display_data(self):
        self.label_WriteData.setHidden(False)
        self.label_Text.setHidden(False)
        self.lineEdit_WriteData.setHidden(False)

    def Hide_data(self):
        self.label_WriteData.setHidden(True)
        self.label_Text.setHidden(True)
        self.lineEdit_WriteData.setHidden(True)

    def display_SSID(self):
        self.comboBox_SSID.clear()
        self.comboBox_SSID.setHidden(False)
        self.label_SSID.setHidden(False)

    def Hide_SSID(self):
        self.comboBox_SSID.clear()
        self.comboBox_SSID.setHidden(True)
        self.label_SSID.setHidden(True)

    def display_DID(self):
        self.comboBox_DID.clear()
        self.comboBox_DID.setHidden(False)
        self.label_DID.setHidden(False)

    def Hide_DID(self):
        self.comboBox_DID.clear()
        self.comboBox_DID.setHidden(True)
        self.label_DID.setHidden(True)
    def add_comboBox_DID(self):
        self.comboBox_DID.addItem("0xF187-零部件编号")
        self.comboBox_DID.addItem("0xF18A-供应商代码")
        self.comboBox_DID.addItem("0xF18B-ECU制造日期")
        self.comboBox_DID.addItem("0xF18C-ECU流水编号")
        self.comboBox_DID.addItem("0xF190-车身号码VIN")
        self.comboBox_DID.addItem("0xF192-供应商ECU硬件号")
        self.comboBox_DID.addItem("0xF193-供应商ECU硬件版本号")
        self.comboBox_DID.addItem("0xF194-供应商ECU软件号")
        self.comboBox_DID.addItem("0xF195-供应商ECU软件版本号")
        self.comboBox_DID.addItem("0xF198-维修点代码或诊断仪序列号")
        self.comboBox_DID.addItem("0xF19D-ECU安装日期代码")

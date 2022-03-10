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
import main
import os


# class Sevice_calss:
def sevice_10(self):
    # print("aaa")
    content = self.comboBox_SSID.currentText()
    if "0x01-默认会话" in content:
        # print("choice 默认会话")
        resp = self.udsclient.change_session(1)
    elif "0x02-编程会话" in content:
        # print("choice 编程会话")
        resp = self.udsclient.change_session(2)
    elif "0x03-扩展会话" in content:
        # print("choice 扩展会话")
        resp = self.udsclient.change_session(3)


def sevice_14(self):
    # print("aaa")
    content = self.comboBox_SSID.currentText()
    if "0x01-硬件复位" in content:
        # print("choice 默认会话")
        resp = self.udsclient.ecu_reset(1)
    elif "0x02-钥匙开关复位" in content:
        # print("choice 编程会话")
        resp = self.udsclient.ecu_reset(2)
    elif "0x03-软件复位" in content:
        # print("choice 扩展会话")
        resp = self.udsclient.ecu_reset(3)


def sevice_19(self):
    # print("aaa")
    content = self.comboBox_SSID.currentText()
    if "0x01-报告DTC数目" in content:
        response = self.udsclient.get_number_of_dtc_by_status_mask(0)  # 通过状态掩码报告DTC数目
    elif "0x02-报告DTC" in content:
        response = self.udsclient.get_dtc_by_status_mask(1)  # 通过状态掩码报告DTC
    elif "0x0A-报告支持的DTC" in content:
        response = self.udsclient.get_supported_dtc()  # 报告支持的DTC
    # response = self.udsclient.get_dtc_snapshot_by_dtc_number()#没有试
    # print(response)


def sevice_22(self):
    print("aaa")
    content = self.comboBox_DID.currentText()
    self.display_rec_data()
    if "0xF187-零部件编号" in content:
        response = self.udsclient.read_data_by_identifier(0xF187)
        self.label_rec_data.setText(str(response.data[2:]))

    elif "0xF18A-供应商代码" in content:
        response = self.udsclient.read_data_by_identifier(0xF18A)
        self.label_rec_data.setText(str(response.data[2:]))
    elif "0xF18B-ECU制造日期" in content:
        response = self.udsclient.read_data_by_identifier(0xF18B)
        self.label_rec_data.setText(str(response.data[2:]))
    elif "0xF18C-ECU流水编号" in content:
        response = self.udsclient.read_data_by_identifier(0xF18C)
        self.label_rec_data.setText(str(response.data[2:]))
    elif "0xF190-车身号码VIN" in content:
        response = self.udsclient.read_data_by_identifier(0xF190)
        self.label_rec_data.setText(str(response.data[2:]))
    elif "0xF192-供应商ECU硬件号" in content:
        response = self.udsclient.read_data_by_identifier(0xF192)
        self.label_rec_data.setText(str(response.data[2:]))
    elif "0xF193-供应商ECU硬件版本号" in content:
        response = self.udsclient.read_data_by_identifier(0xF193)
        self.label_rec_data.setText(str(response.data[2:]))
    elif "0xF194-供应商ECU软件号" in content:
        response = self.udsclient.read_data_by_identifier(0xF194)
        self.label_rec_data.setText(str(response.data[2:]))
    elif "0xF195-供应商ECU软件版本号" in content:
        response = self.udsclient.read_data_by_identifier(0xF195)
        self.label_rec_data.setText(str(response.data[2:]))
    elif "0xF198-维修点代码或诊断仪序列号" in content:
        response = self.udsclient.read_data_by_identifier(0xF198)
        self.label_rec_data.setText(str(response.data[2:]))
    elif "0xF19D-ECU安装日期代码" in content:
        response = self.udsclient.read_data_by_identifier(0xF19D)
        self.label_rec_data.setText(str(response.data[2:]))


def sevice_27(self):
    print("aaa")


def sevice_28(self):
    print("aaa")


def sevice_2E(self):
    content = self.comboBox_DID.currentText()
    write_data = self.lineEdit_WriteData.text()
    if "0xF187-零部件编号" in content:
        if len(write_data) != 10:
            qw.QMessageBox.information(self, "提示", "数据长度错误", qw.QMessageBox.Ok)
            return
        # format_data = list(write_data)
        # # print(format_data)
        # format_data = tuple(format_data)
        # print(format_data)
        write_data=write_data.encode('utf-8')
        print(write_data)
        response = self.udsclient.change_session(3)
        response = self.udsclient.write_data_by_identifier(did=0xF187, value=write_data)
        print(response)
        response = self.udsclient.change_session(1)
    elif "0xF18A-供应商代码" in content:
        pass
    elif "0xF18B-ECU制造日期" in content:
        pass
    elif "0xF18C-ECU流水编号" in content:
        pass
    elif "0xF190-车身号码VIN" in content:
        if len(write_data) != 17:
            qw.QMessageBox.information(self, "提示", "数据长度错误", qw.QMessageBox.Ok)
            return
        write_data = write_data.encode('utf-8')
        response = self.udsclient.change_session(3)
        response = self.udsclient.unlock_security_access(0x01)
        response = self.udsclient.write_data_by_identifier(did=0xF190, value=write_data)
        response = self.udsclient.change_session(1)
    elif "0xF192-供应商ECU硬件号" in content:
        pass
    elif "0xF193-供应商ECU硬件版本号" in content:
        pass
    elif "0xF194-供应商ECU软件号" in content:
        pass
    elif "0xF195-供应商ECU软件版本号" in content:
        pass
    elif "0xF198-维修点代码或诊断仪序列号" in content:
        if len(write_data) != 16:
            qw.QMessageBox.information(self, "提示", "数据长度错误", qw.QMessageBox.Ok)
            return
        write_data = write_data.encode('utf-8')
        response = self.udsclient.change_session(3)
        response = self.udsclient.unlock_security_access(0x01)
        response = self.udsclient.write_data_by_identifier(did=0xF190, value=write_data)
        response = self.udsclient.change_session(1)
    elif "0xF19D-ECU安装日期代码" in content:
        if len(write_data) != 8:
            qw.QMessageBox.information(self, "提示", "数据长度错误", qw.QMessageBox.Ok)
            return
        data = list(write_data)
        for value in data:
            if value > '9' or value < '0':
                qw.QMessageBox.information(self, "提示", "时间输入错误", qw.QMessageBox.Ok)
                return
        timevalue = [int(data[0]),int(data[1]),int(data[2]),int(data[3]),int(data[4]),int(data[5]),int(data[6]),int(data[7])]
        timevalue =tuple(timevalue)
        response = self.udsclient.change_session(3)
        response = self.udsclient.unlock_security_access(0x01)
        response = self.udsclient.write_data_by_identifier(did=0xF19D, value=timevalue)
        response = self.udsclient.change_session(1)
def sevice_3E(self):
    print("aaa")


def sevice_85(self):
    print("aaa")

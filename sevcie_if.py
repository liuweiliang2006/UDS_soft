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
        resp =self.udsclient.change_session(1)
    elif "0x02-编程会话" in content:
        # print("choice 编程会话")
        resp =self.udsclient.change_session(2)
    elif "0x03-扩展会话" in content:
        # print("choice 扩展会话")
        resp = self.udsclient.change_session(3)
def sevice_14(self):
    # print("aaa")
    content = self.comboBox_SSID.currentText()
    if "0x01-硬件复位" in content:
        # print("choice 默认会话")
        resp =self.udsclient.ecu_reset(1)
    elif "0x02-钥匙开关复位" in content:
        # print("choice 编程会话")
        resp =self.udsclient.ecu_reset(2)
    elif "0x03-软件复位" in content:
        # print("choice 扩展会话")
        resp = self.udsclient.ecu_reset(3)

def sevice_19(self):
    # print("aaa")
    content = self.comboBox_SSID.currentText()
    if "0x01-报告DTC数目" in content:
        response = self.udsclient.get_number_of_dtc_by_status_mask(0)  # 通过状态掩码报告DTC数目
    elif  "0x02-报告DTC" in content:
        response = self.udsclient.get_dtc_by_status_mask(1)  # 通过状态掩码报告DTC
    elif "0x0A-报告支持的DTC" in content:
        response = self.udsclient.get_supported_dtc()  # 报告支持的DTC
    # response = self.udsclient.get_dtc_snapshot_by_dtc_number()#没有试
    # print(response)
def sevice_22(self):
    print("aaa")
def sevice_27(self):
    print("aaa")
def sevice_28(self):
    print("aaa")
def sevice_2E(self):
    print("aaa")
def sevice_3E(self):
    print("aaa")
def sevice_85(self):
    print("aaa")
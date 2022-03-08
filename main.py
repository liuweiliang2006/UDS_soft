# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
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
import UDS_sevice as UDS
import PyQt5.QtCore as qc
import udssoft
import Can_sevice
import os

GRPBOX_WIDTH    = 200

DIAG_HEIGHT = 470
DIAG_WIDTH = 500

WIDGHT_WIDTH    = GRPBOX_WIDTH + DIAG_WIDTH + 30
WIDGHT_HEIGHT   = DIAG_HEIGHT + 100

MAX_RCV_NUM     = 20

USBCANFD_TYPE    = (41, 42, 43)
USBCAN_XE_U_TYPE = (20, 21, 31)
USBCAN_I_II_TYPE = (3, 4)

ESC_TX_ID = 0x718
# ESC_TX_ID = 0x748
ESC_RX_ID_PHYS = 0x710
ESC_RX_ID_FUNC = 0x7DF

EPS_TX_ID = 0x73D
EPS_RX_ID_PHYS = 0x718

EPS4wd_TX_ID = 0x7BD
EPS4wd_RX_ID_PHYS = 0x7B5

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
class ZCAN_CCDiag(object):
    class IsoTpConnection(BaseConnection):

        mtu = 4095

        def __init__(self, isotp_layer, name=None):
            BaseConnection.__init__(self, name)
            self.toIsoTPQueue = queue.Queue()
            self.fromIsoTPQueue = queue.Queue()
            self._read_thread = None
            self.exit_requested = False
            self.opened = False
            self.isotp_layer = isotp_layer

            assert isinstance(self.isotp_layer, isotp.TransportLayer) , 'isotp_layer must be a valid isotp.TransportLayer '

        def open(self):
            self.exit_requested = False
            self._read_thread = threading.Thread(None, target=self.rxthread_task)
            self._read_thread.start()
            self.opened = True
            self.logger.info('Connection opened')
            return self

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            self.close()

        def is_open(self):
            return self.opened

        def close(self):
            self.empty_rxqueue()
            self.empty_txqueue()
            self.exit_requested=True
            self._read_thread.join()
            self.isotp_layer.reset()
            self.opened = False
            self.logger.info('Connection closed')

        def specific_send(self, payload):
            if self.mtu is not None:
                if len(payload) > self.mtu:
                    self.logger.warning("Truncating payload to be set to a length of %d" % (self.mtu))
                    payload = payload[0:self.mtu]

            self.toIsoTPQueue.put(bytearray(payload)) # isotp.protocol.TransportLayer uses byte array. udsoncan is strict on bytes format

        def specific_wait_frame(self, timeout=2):
            if not self.opened:
                raise RuntimeError("Connection is not open")

            timedout = False
            frame = None
            try:
                frame = self.fromIsoTPQueue.get(block=True, timeout=timeout)
            except queue.Empty:
                timedout = True

            if timedout:
                raise TimeoutException("Did not receive frame IsoTP Transport layer in time (timeout=%s sec)" % timeout)

            if self.mtu is not None:
                if frame is not None and len(frame) > self.mtu:
                    self.logger.warning("Truncating received payload to a length of %d" % (self.mtu))
                    frame = frame[0:self.mtu]

            return bytes(frame)	# isotp.protocol.TransportLayer uses bytearray. udsoncan is strict on bytes format

        def empty_rxqueue(self):
            while not self.fromIsoTPQueue.empty():
                self.fromIsoTPQueue.get()

        def empty_txqueue(self):
            while not self.toIsoTPQueue.empty():
                self.toIsoTPQueue.get()

        def rxthread_task(self):
            while not self.exit_requested:
                try:
                    self.logger.debug("toIsoTPQueue queue size is now %d" % (self.toIsoTPQueue.qsize()))
                    while not self.toIsoTPQueue.empty():
                        self.isotp_layer.send(self.toIsoTPQueue.get())

                    self.isotp_layer.process()

                    while self.isotp_layer.available():
                        self.fromIsoTPQueue.put(self.isotp_layer.recv())
                    self.logger.debug("fromIsoTPQueue queue size is now %d" % (self.fromIsoTPQueue.qsize()))

                    time.sleep(self.isotp_layer.sleep_time())
                    time.sleep(0.0001)

                except Exception as e:
                    self.exit_requested = True
                    self.logger.error(str(e))
                    print("Error occurred while read CAN(FD) data!")

    def getDateTimeBytes(self):
        """
        get year/month/day and convert into bytes
        """
        _year_high = int(str(datetime.datetime.now().year), 16) >> 8
        _year_low = int(str(datetime.datetime.now().year), 16) & 0xFF
        _month = int(str(datetime.datetime.now().month), 16)
        _day = int(str(datetime.datetime.now().day), 16)
        _hour = int(str(datetime.datetime.now().hour), 16)
        _minute = int(str(datetime.datetime.now().minute), 16)
        _second = int(str(datetime.datetime.now().second), 16)

        return (_year_high, _year_low, _month, _day, _hour, _minute, _second)

    def __init__(self):
        self.DeviceInit()

    def DeviceInit(self):
        self._zcan = ZCAN()
        self._dev_handle = INVALID_DEVICE_HANDLE
        self._can_handle = INVALID_CHANNEL_HANDLE

        # self._isOpen = False
        self._isChnOpen = False

        #current device info
        self._is_canfd = False
        self._res_support = False

        # read can/canfd message thread
        # self._read_thread = None
        self._terminated = False
        self._lock = threading.RLock()

        self.isotp_params = {
            'stmin' : 20,                          # Will request the sender to wait 32ms between consecutive frame. 0-127ms or 100-900ns with values from 0xF1-0xF9
            'blocksize' : 8,                       # Request the sender to send 8 consecutives frames before sending a new flow control message
            'wftmax' : 0,                          # Number of wait frame allowed before triggering an error
            'tx_data_length' : 8,                  # Link layer (CAN layer) works with 8 byte payload (CAN 2.0)
            'tx_padding' : 0,                      # Will pad all transmitted CAN messages with byte 0x00. None means no padding
            'rx_flowcontrol_timeout' : 2000,        # Triggers a timeout if a flow control is awaited for more than 1000 milliseconds
            'rx_consecutive_frame_timeout' : 2000,  # Triggers a timeout if a consecutive frame is awaited for more than 1000 milliseconds
            'squash_stmin_requirement' : False     # When sending, respect the stmin requirement of the receiver. If set to True, go as fast as possible.
            }


        self._isotpaddr_PHYS = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=ESC_RX_ID_PHYS, rxid=ESC_TX_ID)
        self._isotpaddr_FUNC = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=ESC_RX_ID_FUNC, rxid=ESC_TX_ID)

        self.isotp_layer = isotp.TransportLayer(rxfn=self.isotp_rcv, txfn=self.isotp_send, address=self._isotpaddr_PHYS,
                                            params=self.isotp_params)


        self.conn = ZCAN_CCDiag.IsoTpConnection(isotp_layer=self.isotp_layer)
        self.udsclient = Client(self.conn, request_timeout=2)
        self.udsclient.config['p2_timeout'] == 3
        self.udsclient.config['security_algo'] = self.SecAlgo
        self.udsclient.config['security_algo_params'] = [0x4FE87269, 0x6BC361D8, 0x9B127D51, 0x5BA41903]
        self.udsclient.config['data_identifiers'] = {
            0xF1A8 : udsoncan.DidCodec('B'),
            0xF190 : udsoncan.DidCodec('BBBBBBBBBBBBBBBBB'),       # Codec that read ASCII string. We must tell the length of the string
            # 0xF190: udsoncan.AsciiCodec(17),
            0xF195 : udsoncan.DidCodec('B'),
            0xF199 : udsoncan.DidCodec('BBBBBBB')
            }
        self.udsclient.config['server_address_format'] = 32
        self.udsclient.config['server_memorysize_format'] = 32

        ret = self._zcan.OpenDevice(ZCAN_USBCAN2, 0, 0)
        if ret != ZCAN_STATUS_OK:
            print("open can device err")
            exit(0)
        else:
            print("open can device OK")

        iniconfig = ZCAN_CHANNEL_CAN_INIT_CONFIG()
        # iniconfig.acc_code = 0x00000000
        iniconfig.acc_code = 0xE3000000
        iniconfig.acc_mask = 0x00000000
        # iniconfig.acc_mask = 0x718
        iniconfig.filter = 1
        iniconfig.timing0 = 0x00
        iniconfig.timing1 = 0x1C
        iniconfig.mode = 0
        # self.SecAlgo(level = 0x01,seed = [0x2B,0x3A,0x7A,0x44],params =0)
        ret = self._zcan.InitCAN(ZCAN_USBCAN2, 0, 0, iniconfig)
        if ret != ZCAN_STATUS_OK:
            print("init can device err")
            exit(0)
        else:
            print("init can device OK")

        ret = self._zcan.StartCAN(ZCAN_USBCAN2, 0, 0)
        if ret != ZCAN_STATUS_OK:
            print("start can device err")
            exit(0)
        else:
            print("start can device OK")
        # value = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
        # print(type(value))

        self.udsclient.open()
        # payload_send = struct.pack("BBBBBBBB", 0x02, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00)
        # self.conn.send(payload_send)
        # payload_rcv = self.conn.wait_frame(timeout=50)
        # print(payload_rcv)
        # self.udsclient.close()
        # self.isotp_layer = isotp.TransportLayer(rxfn=self.isotp_rcv, txfn=self.isotp_send, address=self._isotpaddr_FUNC,
        #                                         params=self.isotp_params)
        # self.udsclient.open()
        # self.isotp_layer.set_address(self._isotpaddr_FUNC)
        # resp =self.udsclient.change_session(1)
        # print(resp)
        # resp = self.udsclient.write_data_by_identifier(did = 0xF190, value=(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17))
        # print( resp )
        # resp = self.udsclient.read_data_by_identifier(0xF190)
        # print( resp )
        # resp = self.udsclient.request_seed(0x01)
        # self.udsclient.unlock_security_access(0x01)
        # print(resp.data)
        # resp = self.udsclient.read_data_by_identifier(0xF190)
        # resp = self.udsclient.write_data_by_identifier(did=0xF190, value=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17))
        # print(resp)
        # resp = self.udsclient.read_data_by_identifier(0xF190)


    def SecAlgo(self, level, seed, params):
        if level == 0x01:
            mask = 0xEBCAFE17
            # mask = 0x8EACBD9F
        else:
            mask = 0xE75BF4E7
        temp_key = (seed[0] << 24) | (seed[1] << 16) | (seed[2] << 8) | (seed[3])
        for i in range(0,35):
            if temp_key & 0x80000000:
                temp_key = temp_key << 1
                temp_key = temp_key ^ mask
            else:
                temp_key = temp_key << 1
        for i in range(0,4):
            if i == 0:
                key3 = temp_key & 0x000000ff
            if i == 1:
                key2 = (temp_key >> 8) & 0x000000ff
            if i == 2:
                key1 = (temp_key >> 16) & 0x000000ff
            if i == 3:
                key0 = (temp_key >> 24) & 0x000000ff
        key = [key0,key1,key2,key3]
        # key = (key0<<24)|(key1<<16)|(key2<<8)|key3
        # print(hex(key0),hex(key1),hex(key2),hex(key3))
        # print(hex(key))
        key = struct.pack('BBBB',key0,key1,key2,key3)
        return key

    def isotp_rcv(self):
        can_num = self._zcan.GetReceiveNum(ZCAN_USBCAN2, 0, 0)
        if can_num and not self._terminated:
            read_cnt = MAX_RCV_NUM if can_num >= MAX_RCV_NUM else can_num
            can_msgs, act_num = self._zcan.Recvive(ZCAN_USBCAN2, 0, 0, can_num)
            # print("%s"%binascii.hexlify(can_msgs[0].Data))
        else:
            can_msgs = None
        return can_msgs


    def isotp_send(self, isotp_msg):
        # self.isotp_layer = isotp.TransportLayer(rxfn=self.isotp_rcv, txfn=self.isotp_send, address=self._isotpaddr_FUNC,
        #                                         params=self.isotp_params)
        # self.conn = ZCAN_CCDiag.IsoTpConnection(isotp_layer=self.isotp_layer)
        # self.udsclient = Client(self.conn, request_timeout=2)
        #isotp_msg.data.extend(bytearray([0xCC] * (8-len(isotp_msg.data))))
        # msg = ZCAN_Transmit_Data()

        msg = ZCAN_CAN_OBJ()
        # msg.transmit_type = 0 #正常发送
        msg.ID = isotp_msg.arbitration_id
        msg.SendType = 1
        msg.RemoteFlag = 0
        msg.ExternFlag = 0
        msg.DataLen = isotp_msg.dlc
        #msg.frame.can_dlc = 8

        for i in range(len(isotp_msg.data)):
            msg.Data[i] = isotp_msg.data[i]
        print("sed:id-%s,dlc-%d,data-%s" % (hex(msg.ID), msg.DataLen, binascii.hexlify(msg.Data)))
        # print(str(datetime.datetime.now().second))
        # print(str(datetime.datetime.now().microsecond))
        ret = self._zcan.Transmit(ZCAN_USBCAN2, 0, 0, msg, 1)
        if ret != 1:
            # messagebox.showerror(title="发送报文", message="发送失败！")
            print("发送失败")
        return




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = qw.QApplication(sys.argv)
    w = UDS.myMainWindow()
    # recv_can_msgs = (ZCAN_CAN_OBJ * 10)()
    # recv_can_msgs[0].ID = 1
    # recv_can_msgs[1].ID = 2
    # recv_can_msgs[2].ID = 3
    # print(recv_can_msgs[0].ID)
    # print(recv_can_msgs[1].ID)
    # print(recv_can_msgs[2].ID)
    # demo = ZCAN_CCDiag()
    w.show()
    print_hi('PyCharm')
    sys.exit(app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

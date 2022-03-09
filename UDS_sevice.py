import binascii
import datetime
import queue
import struct
import threading
import time

from PyQt5.QtWidgets import  *

from ControlCAN import *
from udsoncan.client import Client
from udsoncan.exceptions import TimeoutException
import udsoncan
from udsoncan.connections import BaseConnection

import isotp


import PyQt5.QtWidgets as qw
import sevcie_if
import udssoft

q= queue.Queue()

MAX_RCV_NUM     = 20
class myMainWindow(qw.QMainWindow,udssoft.Ui_MainWindow):
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
            rec_msg = ZCAN_CAN_OBJ()
            while not self.exit_requested:
                try:
                    self.logger.debug("toIsoTPQueue queue size is now %d" % (self.toIsoTPQueue.qsize()))
                    while not self.toIsoTPQueue.empty():
                        self.isotp_layer.send(self.toIsoTPQueue.get())

                    msg = self.isotp_layer.process()
                    if msg != None:
                        rec_msg.ID = msg.arbitration_id
                        rec_msg.SendType = 1
                        rec_msg.RemoteFlag = 0
                        rec_msg.ExternFlag = 0
                        rec_msg.DataLen = msg.dlc
                        rec_msg.Data = msg.data
                        # print(hex(msg.arbitration_id))
                        q.put(rec_msg)
                        # w.display(,msgs=rec_msg)
                        # main.w.display(msgs=rec_msg)

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
        super().__init__()#继承父类的方式实例化子类
        self.setupUi(self)
        # self._read_thread = threading.Thread(None, target=self.rxthread_task)
        self.rec = threading.Thread(None, target=self.rec_task)
        self.rec.start()
        #初始化默认参数
        self._zcan = ZCAN()
        self._dev_handle = INVALID_DEVICE_HANDLE
        self._can_handle = INVALID_CHANNEL_HANDLE
        self._isOpen = False
        self._isChnOpen = False
        # current device info
        self._is_canfd = False
        self._res_support = False
        # read can/canfd message thread
        # self._read_thread = None
        self._terminated = False
        self._lock = threading.RLock()
        # self.comboBox_SID.setCurrentText("0x11 - EcuReset")
        # self.comboBox_SID.setCurrentText("0x10-DiagnosticSessionControl")

        self.isotp_params = {
            'stmin': 20,            # Will request the sender to wait 32ms between consecutive frame. 0-127ms or 100-900ns with values from 0xF1-0xF9
            'blocksize': 8,         # Request the sender to send 8 consecutives frames before sending a new flow control message
            'wftmax': 0,            # Number of wait frame allowed before triggering an error
            'tx_data_length': 8,    # Link layer (CAN layer) works with 8 byte payload (CAN 2.0)
            'tx_padding': 0,        # Will pad all transmitted CAN messages with byte 0x00. None means no padding
            'rx_flowcontrol_timeout': 2000,           # Triggers a timeout if a flow control is awaited for more than 1000 milliseconds
            'rx_consecutive_frame_timeout': 2000,     # Triggers a timeout if a consecutive frame is awaited for more than 1000 milliseconds
            'squash_stmin_requirement': False         # When sending, respect the stmin requirement of the receiver. If set to True, go as fast as possible.
        }
        # 初始化界面
        self.radioButton_phy.setChecked(True)

        titles = ['系统时间', '传输方向', 'ID号', ' 数据']
        self.tableWidget = QTableWidget(self.tableWidget)   #创建空表格
        self.tableWidget.resize(1051,301)
        #self.table = QTableWidget(4,3,self)  #创建4行3列的表格
        # self.tableWidget.setRowCount(100)  # 设置行数--不包括标题列
        self.tableWidget.setColumnCount(4)  # 设置列数
        self.tableWidget.setHorizontalHeaderLabels(titles)  # 标题列---水平标题
        # self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tableWidget.setColumnWidth(4, 350)#设置某列的宽度
        self.tableWidget.horizontalHeader().setStretchLastSection(True)#设置最后一列自动填充容器
        # self.tableWidget.setItem(0, 2, QTableWidgetItem("0x01"))
        # 信号与槽
        self.comboBox_SID.currentTextChanged.connect(self.comboBox_SID_cb)
        self.pushButton_Open.clicked.connect(self.pushButton_Open_cb)
        self.pushButton_Close.clicked.connect(self.pushButton_Close_cb)
        # self.lineEdit_AddrPHY.editingFinished.connect(self.lineEdit_AddrPHY_cb)
        self.pushButton_AddrSet.clicked.connect(self.pushButton_AddrSet_cb)
        self.radioButton_phy.toggled.connect(self.pushButton_AddrSet_cb)
        self.pushButton_send.clicked.connect(self.pushButton_send_cb)
    def comboBox_SID_cb(self):
        content = self.comboBox_SID.currentText()
        print("combox's value is", content)
        if "NONE" in content:
            self.display_data()
            self.display_SSID()
            self.display_DID()

        if "0x10" in content:
            print("0x10")
            self.SID_Value=0x10
            self.display_SSID()
            self.Hide_data()
            self.Hide_DID()
            self.comboBox_SSID.addItem("0x01-默认会话")
            self.comboBox_SSID.addItem("0x02-编程会话")
            self.comboBox_SSID.addItem("0x03-扩展会话")

        if "0x11" in content:
            print("0x11")
            self.SID_Value = 0x11
            self.display_SSID()
            self.Hide_data()
            self.Hide_DID()
            self.comboBox_SSID.addItem("0x01-硬件复位")
            self.comboBox_SSID.addItem("0x02-钥匙开关复位")
            self.comboBox_SSID.addItem("0x03-软件复位")
        if "0x14" in content:
            print("0x14")
            self.SID_Value = 0x14
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
            self.SID_Value = 0x19
            self.display_SSID()
            self.Hide_data()
            self.Hide_DID()
            self.comboBox_SSID.addItem("0x01-报告DTC数目")
            self.comboBox_SSID.addItem("0x02-报告DTC")
            # self.comboBox_SSID.addItem("0x04-DTCSnapshot记录")
            # self.comboBox_SSID.addItem("0x06-DTC扩展数据记录")
            self.comboBox_SSID.addItem("0x0A-报告支持的DTC")
        if "0x22" in content:
            print("0x22")
            self.SID_Value = 0x22
            self.Hide_SSID()
            self.Hide_data()
            self.display_DID()
            self.add_comboBox_DID()
            # self.comboBox_SSID.setEditable(False)
        if "0x23" in content:
            print("0x23")
        if "0x27" in content:
            print("0x27")
            self.SID_Value = 0x27
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
            self.SID_Value = 0x28
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
            self.SID_Value = 0x2E
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
            self.SID_Value = 0x3E
            self.display()
            self.comboBox_SSID.setHidden(True)
            self.label_SSID.setHidden(True)

        if "0x85" in content:
            print("0x85")
            self.SID_Value = 0x85
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


    def pushButton_Open_cb(self):
        print("open_cb")
        # ZCAN_CCDiag._isOpen
        if self._isOpen:
            qw.QMessageBox.information(self, "提示", "opened!", qw.QMessageBox.Ok )
        else:
            ret = self._zcan.OpenDevice(ZCAN_USBCAN2, 0, 0)
            if ret != ZCAN_STATUS_OK:
                qw.QMessageBox.information(self, "提示", "打开失败", qw.QMessageBox.Ok)
            else:
                qw.QMessageBox.information(self, "提示", "打开成功", qw.QMessageBox.Ok)

            iniconfig = ZCAN_CHANNEL_CAN_INIT_CONFIG()
            acc_code = self.lineEdit_AccCode.text()
            acc_code = int(acc_code,base=16)
            acc_mask = self.lineEdit_AccMask.text()
            acc_mask = int(acc_mask,base=16)
            # print(hex(acc_mask))
            iniconfig.acc_code = acc_code
            iniconfig.acc_mask = acc_mask
            iniconfig.filter = 1
            iniconfig.timing0 = 0x00
            iniconfig.timing1 = 0x1C
            iniconfig.mode = 0
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

            self._isOpen = True



    def pushButton_Close_cb(self):
        self._isOpen = False

    def pushButton_AddrSet_cb(self):
        if self.radioButton_phy.isChecked():
            self.uds_tp_phy_set()
        if self.radioButton_Func.isChecked():
            self.uds_tp_func_set()
        self.uds_udsclient_config()

    # def radioButton_phy_cb(self):
    #     if self.radioButton_phy.isChecked():
    #         self.uds_tp_phy_set()
    #     else:
    #         self.uds_tp_func_set()
    #     self.uds_udsclient_config()

    def uds_tp_phy_set(self):
        phy_addr = self.lineEdit_AddrPHY.text()
        phy_addr = int(phy_addr, base=16)
        res_addr = self.lineEdit_AddrRes.text()
        res_addr = int(res_addr, base=16)
        self._isotpaddr_PHYS = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=phy_addr, rxid=res_addr)
        self.isotp_layer = isotp.TransportLayer(rxfn=self.isotp_rcv, txfn=self.isotp_send,
                                                address=self._isotpaddr_PHYS,
                                                params=self.isotp_params)
        # print("radioButton_PHY")

    def uds_tp_func_set(self):
        func_addr = self.lineEdit_AddrFunc.text()
        func_addr = int(func_addr, base=16)
        res_addr = self.lineEdit_AddrRes.text()
        res_addr = int(res_addr, base=16)
        self._isotpaddr_FUNC = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=func_addr, rxid=res_addr)
        self.isotp_layer = isotp.TransportLayer(rxfn=self.isotp_rcv, txfn=self.isotp_send,
                                                address=self._isotpaddr_FUNC,
                                                params=self.isotp_params)

        print("radioButton_Func")

    def uds_udsclient_config(self):
        self.conn = myMainWindow.IsoTpConnection(isotp_layer=self.isotp_layer)
        self.udsclient = Client(self.conn, request_timeout=2)

        self.udsclient.config['p2_timeout'] = 3
        self.udsclient.config['security_algo'] = self.SecAlgo
        self.udsclient.config['security_algo_params'] = [0x4FE87269, 0x6BC361D8, 0x9B127D51, 0x5BA41903]
        self.udsclient.config['data_identifiers'] = {
            0xF1A8: udsoncan.DidCodec('B'),
            0xF190: udsoncan.DidCodec('BBBBBBBBBBBBBBBBB'),
            # Codec that read ASCII string. We must tell the length of the string
            # 0xF190: udsoncan.AsciiCodec(17),
            0xF195: udsoncan.DidCodec('B'),
            0xF199: udsoncan.DidCodec('BBBBBBB')
        }
        self.udsclient.config['server_address_format'] = 32
        self.udsclient.config['server_memorysize_format'] = 32
        self.udsclient = Client(self.conn, config=self.udsclient.config, request_timeout=2)

    def pushButton_send_cb(self):
        print("sendbutton")
        self.udsclient.open()
        if self.SID_Value == 0x10:
            # print("sevice - 0x10")
            sevcie_if.sevice_10(self)
        elif self.SID_Value ==0x11:
            sevcie_if.sevice_11(self)
        elif self.SID_Value ==0x14:
            sevcie_if.sevice_14(self)
        elif self.SID_Value ==0x19:
            sevcie_if.sevice_19(self)
        elif self.SID_Value ==0x22:
            sevcie_if.sevice_22(self)
        elif self.SID_Value ==0x27:
            sevcie_if.sevice_27(self)
        elif self.SID_Value ==0x28:
            sevcie_if.sevice_28(self)
        elif self.SID_Value ==0x2E:
            sevcie_if.sevice_2E(self)
        elif self.SID_Value ==0x3E:
            sevcie_if.sevice_3E(self)
        elif self.SID_Value ==0x85:
            sevcie_if.sevice_85(self)

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
        msg.ID = isotp_msg.arbitration_id
        msg.SendType = 1
        msg.RemoteFlag = 0
        msg.ExternFlag = 0
        msg.DataLen = isotp_msg.dlc

        for i in range(len(isotp_msg.data)):
            msg.Data[i] = isotp_msg.data[i]
        # print("sed:id-%s,dlc-%d,data-%s" % (hex(msg.ID), msg.DataLen, binascii.hexlify(msg.Data)))


        self.display(msgs = msg,direction=2)

        # print(str(datetime.datetime.now().second))
        # print(str(datetime.datetime.now().microsecond))
        ret = self._zcan.Transmit(ZCAN_USBCAN2, 0, 0, msg, 1)
        if ret != 1:
            # messagebox.showerror(title="发送报文", message="发送失败！")
            print("发送失败")
        return

    def display(self, msgs,direction):
        # print(self)
        row_count = self.tableWidget.rowCount()
        if row_count >= 100:
            self.tableWidget.removeRow(0)
        self.tableWidget.insertRow(row_count)

        can_data = []
        i = 0
        while i < msgs.DataLen:
            can_data.append(hex(msgs.Data[i]))
            i = i + 1
        self.tableWidget.setItem(row_count, 2, QTableWidgetItem(str(hex(msgs.ID))))
        self.tableWidget.setItem(row_count, 3, QTableWidgetItem(str(can_data)))
        if direction==2:
            self.tableWidget.setItem(row_count, 1, QTableWidgetItem("TX"))
        elif direction==1:
            self.tableWidget.setItem(row_count, 1, QTableWidgetItem("RX"))

    def rec_task(self):
        while True:
            # print("rec_task")
            revmsg = q.get()
            if revmsg != None:
                # print("REV:id-%s,dlc-%d,data-%s" % (hex(revmsg.ID), revmsg.DataLen, binascii.hexlify(revmsg.Data)))
                # print(revmsg.DataLen)
                # print(revmsg.ID)
                self.display(msgs=revmsg,direction=1)
            time.sleep(0.0001)

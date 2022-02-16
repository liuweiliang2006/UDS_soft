from ctypes import *
import platform
from udsoncan.client import Client
from udsoncan.exceptions import TimeoutException
import udsoncan
from udsoncan.connections import BaseConnection
from udsoncan import services, Response, MemoryLocation

import isotp
from isotp import CanMessage
from functools import partial

import os

INVALID_DEVICE_HANDLE  = 0
INVALID_CHANNEL_HANDLE = 0

#os.add_dll_directory(r"C:\Users\user\Desktop\ZLG\zlgcan_demo\zlgcan_python")

'''
Device Type
'''
#设备类型选择--根据广州致远电子有限公司  CAN测试软件和接口函数使用手册
ZCAN_PCI5121          = c_uint(1)
ZCAN_PCI98101         = c_uint(2)
ZCAN_USBCAN1          = c_uint(3)
ZCAN_USBCAN2          = c_uint(4)

'''
 Interface return status
'''
ZCAN_STATUS_ERR         = 0
ZCAN_STATUS_OK          = 1
ZCAN_STATUS_ONLINE      = 2
ZCAN_STATUS_OFFLINE     = 3
ZCAN_STATUS_UNSUPPORTED = 4

'''
 Device information
'''

'''
board info
'''
class ZCAN_BOARD_INFO(Structure):
    _fields_ = [("hw_Version", c_ushort),
                ("fw_Version", c_ushort),
                ("dr_Version", c_ushort),
                ("in_Version", c_ushort),
                ("irq_Num", c_ushort),
                ("can_Num", c_ubyte),
                ("str_Serial_Num", c_ubyte * 20),
                ("str_hw_Type", c_ubyte * 40),
                ("reserved", c_ushort * 4)]

    def __str__(self):
        return "Hardware Version:%s\nFirmware Version:%s\nDriver Interface:%s\nInterface Interface:%s\nInterrupt Number:%d\nCAN Number:%d\nSerial:%s\nHardware Type:%s\n" % ( \
            self.hw_version, self.fw_version, self.dr_version, self.in_version, self.irq_num, self.can_num, self.serial,
            self.hw_type)

    def _version(self, version):
        return ("V%02x.%02x" if version // 0xFF >= 9 else "V%d.%02x") % (version // 0xFF, version & 0xFF)

    @property
    def hw_version(self):
        return self._version(self.hw_Version)

    @property
    def fw_version(self):
        return self._version(self.fw_Version)

    @property
    def dr_version(self):
        return self._version(self.dr_Version)

    @property
    def in_version(self):
        return self._version(self.in_Version)

    @property
    def irq_num(self):
        return self.irq_Num

    @property
    def can_num(self):
        return self.can_Num

    @property
    def serial(self):
        serial = ''
        for c in self.str_Serial_Num:
            if c > 0:
                serial += chr(c)
            else:
                break
        return serial

    @property
    def hw_type(self):
        hw_type = ''
        for c in self.str_hw_Type:
            if c > 0:
                hw_type += chr(c)
            else:
                break
        return hw_type

'''
VCI_INIT_CONFIG
'''
class ZCAN_CHANNEL_CAN_INIT_CONFIG(Structure):
    _fields_ = [("acc_code", c_uint),
                ("acc_mask", c_uint),
                ("reserved", c_uint),
                ("filter",   c_ubyte),
                ("timing0",  c_ubyte),
                ("timing1",  c_ubyte),
                ("mode",     c_ubyte)]

'''
VCI_ERR_INFO
@1 错误码
@2 当产生的错误中有消极错误时表示为消极错误的错误标识数据
@3 当产生的错误中有仲裁丢失错误时表示为仲裁丢失错误的错误标识数据。
'''
class ZCAN_CHANNEL_ERR_INFO(Structure):
    _fields_ = [("error_code", c_uint),
                ("passive_ErrData", c_ubyte * 3),
                ("arLost_ErrData", c_ubyte)]

'''
VCI_CAN_STATUS
'''
class ZCAN_CHANNEL_STATUS(Structure):
    _fields_ = [("errInterrupt", c_ubyte),
                ("regMode",      c_ubyte),
                ("regStatus",    c_ubyte),
                ("regALCapture", c_ubyte),
                ("regECCapture", c_ubyte),
                ("regEWLimit",   c_ubyte),
                ("regRECounter", c_ubyte),
                ("regTECounter", c_ubyte),
                ("Reserved",     c_ubyte)]

'''
VCI_CAN_OBJ
'''

class ZCAN_CAN_OBJ(Structure):
    _fields_ = [("ID",              c_uint),
                ("TimeStamp",       c_uint),
                ("TimeFlag",        c_ubyte),
                ("SendType",        c_ubyte),
                ("RemoteFlag",      c_ubyte),
                ("ExternFlag",      c_ubyte),
                ("DataLen",         c_ubyte),
                ("Data",            c_ubyte*8),
                ("Reserved",        c_ubyte*3)]

class ISOTP_CAN_FRAME(Structure):
    _fields_ = [("arbitration_id",  c_uint),
                ("TimeStamp",       c_uint),
                ("TimeFlag",        c_ubyte),
                ("SendType",        c_ubyte),
                ("RemoteFlag",      c_ubyte),
                ("ExternFlag",      c_ubyte),
                ("dlc",             c_ubyte),
                ("data",            c_ubyte*8),
                ("Reserved",        c_ubyte*3)]

class ZCAN_CAN_FRAME(Structure):
    _fields_ = [("can_id",  c_uint, 29),
                ("err",     c_uint, 1),
                ("rtr",     c_uint, 1),
                ("eff",     c_uint, 1),
                ("can_dlc", c_ubyte),
                ("__pad",   c_ubyte),
                ("__res0",  c_ubyte),
                ("__res1",  c_ubyte),
                ("data",    c_ubyte * 8)]


class ZCAN_Transmit_Data(Structure):
    _fields_ = [("frame", ZCAN_CAN_OBJ), ("transmit_type", c_uint)]

class ZCAN_Receive_Data(Structure):
    _fields_  = [("frame", ZCAN_CAN_OBJ), ("timestamp", c_ulonglong)]

'''
CAN  CLASS
'''
class ZCAN(object):
    def __init__(self):
        if platform.system() == "Windows":
            self.__dll = windll.LoadLibrary("./ControlCAN.dll")
        else:
            print("No support now")

        if self.__dll is None:
            print("load ControlCAN.dll err")
        else:
            print("load ControlCAN.dll OK")

    def OpenDevice(self, device_type, device_index, reserved):
        try:
            ret = self.__dll.VCI_OpenDevice(device_type, device_index, reserved)
            return ret
        except:
            print("except on opendevice")
            raise

    def CloseDevice(self, device_type, device_index):
        try:
            return self.__dll.VCI_CloseDevice(device_type, device_index)
        except:
            print("except on closedevice")
            raise

    def InitCAN(self, device_type, device_index, can_index,init_config):
        try:
            return self.__dll.VCI_InitCAN(device_type, device_index, can_index, pointer(init_config))
        except:
            print("except on InitCAN")
            raise

    def GetBoardinfo(self,device_type, device_index):
        try:
            board_info = ZCAN_BOARD_INFO()
            ret = self.__dll.VCI_ReadBoardInfo(device_type, device_index, byref(board_info))
            return board_info if ret == ZCAN_STATUS_OK else None
        except:
            print("read boardinfo err")
            raise

    def ReadErrInfo(self, device_type, device_index, can_index):
        try:
            errInfo = ZCAN_CHANNEL_ERR_INFO()
            ret = self.__dll.VCI_ReadErrInfo(device_type, device_index, can_index, byref(errInfo))
            return errInfo if ret == ZCAN_STATUS_OK else None
        except:
            print("except on ReadErrInfo")
            raise

    def ReadCanStatus(self,device_type, device_index, can_index):
        try:
            errInfo = ZCAN_CHANNEL_STATUS()
            ret = self.__dll.VCI_ReadCANStatus(device_type, device_index, can_index, byref(errInfo))
            return errInfo if ret == ZCAN_STATUS_OK else None
        except:
            print("except on ReadCanStatus")
            raise

    def StartCAN(self, device_type, device_index, can_index):
        try:
            return self.__dll.VCI_StartCAN(device_type, device_index, can_index)
        except:
            print("except on StartCAN")
            raise

    def ResetCAN(self, device_type, device_index, can_index):
        try:
            return self.__dll.VCI_ResetCAN(device_type, device_index, can_index)
        except:
            print("except on StartCAN")
            raise

    def GetReceiveNum(self,device_type, device_index, can_index):
            try:
                return self.__dll.VCI_GetReceiveNum(device_type, device_index, can_index)
            except:
                print("except on GetReceiveNum")
                raise

    def ClearBuffer(self,device_type, device_index, can_index):
            try:
                return self.__dll.VCI_ClearBuffer(device_type, device_index, can_index)
            except:
                print("except on ClearBuffer")
                raise

    def Transmit(self,device_type, device_index, can_index, std_msg, lenth):
            try:
                return self.__dll.VCI_Transmit(device_type, device_index, can_index, byref(std_msg), lenth)
            except:
                print("except on Transmit")
                raise

    def Recvive(self,device_type, device_index, can_index,rcv_num, wait_time = c_int(-1)):
            try:
                print("rcv_num =",rcv_num)
                recv_can_msgs = (ZCAN_CAN_OBJ * rcv_num)()
                ret = self.__dll.VCI_Receive(device_type, device_index, can_index, byref(recv_can_msgs), rcv_num,wait_time)
                return recv_can_msgs,ret
            except:
                print("except on Transmit")
                raise

#测试代码
if __name__ == "__main__":

    # with open("LEARAD00012.s19", "r") as fd:
    # #     fd = open("LEARAD00012.s19", "r")
    #     t_espsw = fd.readlines()
    #     # print(t_espsw)
    # print("----------------------------------------------------------------------------------------")
    # _espsw = t_espsw[1:-1]
    # # print(_espsw)
    # _espSwPartsNum = 0
    # _espSwParts = []
    # _cutPoint = 0
    # _espDataBatch = {}
    # for i in range(1, len(_espsw)):
    #     if (int(_espsw[i][4:10], 16) - int(_espsw[i - 1][4:10], 16)) != (int(_espsw[i - 1][2:4], 16) - 4):
    #         _espSwParts.append(_espsw[_cutPoint:i])
    #         # print("----------------------------------------------------------------------------------------")
    #         # print(_espSwParts)
    #         _cutPoint = i
    #         _espSwPartsNum += 1
    # _espSwParts.append([_espsw[len(_espsw) - 1]])
    # _espSwPartsNum += 1
    # print(_espSwParts)
    # demo = ZCAN_CCDiag()
    zcanlib = ZCAN()
    ret = zcanlib.OpenDevice(ZCAN_USBCAN2, 0, 0)
    if ret != ZCAN_STATUS_OK:
        print("open can device err")
        exit(0)

    info = zcanlib.GetBoardinfo(ZCAN_USBCAN2, 0)
    print("board infomation: %s" %(info))

    iniconfig = ZCAN_CHANNEL_CAN_INIT_CONFIG()
    iniconfig.acc_code = 0x00000000
    iniconfig.acc_mask = 0xffffffff
    iniconfig.filter = 1
    iniconfig.timing0 = 0x00
    iniconfig.timing1 = 0x1C
    iniconfig.mode = 0
    ret = zcanlib.InitCAN(ZCAN_USBCAN2, 0, 0,iniconfig)
    if ret != ZCAN_STATUS_OK:
        print("init can device err")
        exit(0)

    ret = zcanlib.StartCAN(ZCAN_USBCAN2, 0, 0)
    if ret != ZCAN_STATUS_OK:
        print("start can device err")
        exit(0)

    #send msg
    trams_nums = 10
    msgs = (ZCAN_CAN_OBJ * trams_nums)()
    for i in range(trams_nums):
        msgs[i].ID = 0x123
        msgs[i].SendType = 1
        msgs[i].RemoteFlag = 0
        msgs[i].ExternFlag = 0
        msgs[i].DataLen = 8
        for j in range(msgs[i].DataLen):
            msgs[i].Data[j] = j

    ret = zcanlib.Transmit(ZCAN_USBCAN2, 0, 0, msgs, trams_nums)
    print("ret = %d" % ret)
    sum_recv = 0
    while True:
        try:
            recv_num = zcanlib.GetReceiveNum(ZCAN_USBCAN2, 0, 0)
            if recv_num:
                print("recv_num = %d" % recv_num)
                recv_msg, num = zcanlib.Recvive(ZCAN_USBCAN2, 0, 0, recv_num)
                sum_recv += num
                print("num = ", sum_recv)
                if num>0 and recv_msg is not None:
                    print("num = %d", num)
                    for i in range(num):
                        print("[%d,%d]:ID:%08x, DLC:%d data:%s" %(i, recv_msg[i].TimeStamp, recv_msg[i].ID, \
                                                                 recv_msg[i].DataLen, \
                            ''.join(str(recv_msg[i].Data[j]) + ' ' for j in range(recv_msg[i].DataLen))))

        except:
            print("main err num ")
            raise

    zcanlib.ClearBuffer(ZCAN_USBCAN2, 0, 0)
    zcanlib.CloseDevice(ZCAN_USBCAN2, 0)
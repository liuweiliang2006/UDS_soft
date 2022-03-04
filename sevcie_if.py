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


class Sevice_calss:
    def sevice_10(self):
        print("aaa")
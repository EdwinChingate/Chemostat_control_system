import serial
from time import sleep
import matplotlib.pyplot as plt
import binascii
from time import time
import time	
import PyTrinamic
from PyTrinamic.connections.usb_tmcl_interface import usb_tmcl_interface
from PyTrinamic.connections.tmcl_interface import tmcl_interface
from PyTrinamic.connections.ConnectionManager import ConnectionManager
#from PyTrinamic.conections import tmcl_interface
import numpy as np
import datetime
import os


def Connect(port):
    """connect to the Trinamic controller to allow control of pumps"""
    board = '/dev/Trinamic' + str(port)
    argu = ['--port', board]
    con = ConnectionManager(argList=argu)
    do = con.connect()
    return do
vel2=10
mo=2
port=3
do=Connect(port)
#do.rotate(efluent,-vel)
t0=time.time()
ti=0
do.rotate(mo,2000)
time.sleep(5) 
while True:
#    print(vel1)
#    do.rotate(mo,vel1)
#    time.sleep(0.2)
    print(vel2)
    do.rotate(mo,vel2)
    time.sleep(60*60*60)
    #do.stop(3)
    #time.sleep(9*60*60)
do.stop(mo)

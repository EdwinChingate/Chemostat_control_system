from serial import Serial
#test
from time import sleep
import matplotlib.pyplot as plt
import binascii
from time import time
import time
import PyTrinamic
#from PyTrinamic.connections.usb_tmcl_interface import usb_tmcl_interface
#from PyTrinamic.connections.tmcl_interface import tmcl_interface
from PyTrinamic.connections.ConnectionManager import ConnectionManager
#from PyTrinamic.connections import tmcl_interface
import numpy as np
import datetime
import os
import pandas as pd 
import sys
from serial import SerialException
from os import scandir, getcwd
import shutil

def Cop(old,new): #Coppy files from an old rute to a newone
    #old: full name of the file with the current directory
    #new: new name for the file with the directory wanted
    origen=old
    destino=new
    if os.path.exists(origen):
        with open(origen, 'rb') as forigen:
            with open(destino, 'wb') as fdestino:
                shutil.copyfileobj(forigen, fdestino)

def Main(re):
    re=int(re)-int(1)
    Reac=pd.read_excel('reactors.xlsx',index_col=0)
    Rname=Reac.iloc[:,re].name
    print('Selected reactor: '+Rname)
    file=open(str(re+1)+'.txt','r')    
    Now=file.read()
    file.close()  
    Cop('reactors.xlsx',Now+'/Reactors.xlsx')
    Cop('Experiment.py',Now+'/Experiment'+str(re+1)+'.py')
    Cop('stop.py',Now+'/stop.py')
    
Main(input())

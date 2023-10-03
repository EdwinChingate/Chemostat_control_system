#So I should be able to make comments and keep track of the versions after I marge and accept the changes
from serial import Serial
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
    re=int(re)
    currentDate=str(datetime.datetime.now())[:16].replace(' ','_')
    Reac=pd.read_excel('reactors.xlsx',index_col=0)
   # Rname=str(Reac.iloc[:,re].name)
    print('Selected reactor: '+str(re))
    #print(Reac[Rname])    
    Reac[Rname]['CurrentStart']=currentDate
    Reac.to_excel('reactors.xlsx')
    here=getcwd()
    Colors=here+'/Colors'
    ROp=Colors+'/'+Rname
    Now=ROp+'/'+currentDate
    if os.path.exists(Colors)==False:
        os.mkdir(Colors)
    if os.path.exists(ROp)==False:
        os.mkdir(ROp)
    if os.path.exists(Now)==False:
        os.mkdir(Now)
    Cop('reactors.xlsx',Now+'/Reactors.xlsx')
    Cop('Experiment.py',Now+'/Experiment'+str(re+1)+'.py')
    Cop('stop.py',Now+'/stop.py')
    Cop('data.csv',Now+'/data.csv')
    Cop('error.csv',Now+'/error.csv')
    file=open(str(re+1)+'.txt','w')
    file.write(Now)
    file.close()
    
Main(input())

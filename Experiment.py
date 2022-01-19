from serial import Serial
import binascii
import time
from PyTrinamic.connections.ConnectionManager import ConnectionManager
import datetime
from os import system, getcwd
import pandas as pd 



def saveN(res):
    """convert return value from scale into decimal value"""
    st = str(res)[4:14]
    st = st.replace('\n','')
    st = st.replace('\r','')
    st = st.replace('g','')
    c = ''
    for x in st:
        if (x!=' '):
            c = c+x
    return (c)
    

    
def Scale(scale_num, reactor,error):
    """read and return current value from scale"""
    sca = "/dev/" + scale_num
    while True:
        try:
            ser= Serial(port=sca, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10)
            com = binascii.a2b_hex('77')
            t5 = ser.write(com)
            res = ser.read(15)
            return float(saveN(res))
        except:
            print('Error: ' + scale_num +' disconnected')
            time.sleep(30)
            WritEr('Error: ' + scale_num +' disconnected', error)   

    

def Writ(t0, ScaleR, stage, speede, name, Ob, reactor, error):
    """append important reactor/control parameters to a data file"""
    wr = Scale(ScaleR, reactor, error)
    spde = str(speede)
    timew = str(round((time.time())/60,2))
    Dif = str(round(wr-Ob,1))
    ctime = str(datetime.datetime.now())[0:16]
    log = ctime + ';' + timew + ';' + str(wr) + ';' + str(stage) + ';' + spde + ';' + Dif + '\n'
    file = open(name,'a')
    file.write(log)
    file.close()
    
    
    
def WritEr(write, error):
    """append error message to an error file"""
    ctime = str(datetime.datetime.now())[0:16]
    log = ctime + ';' + write + '\n'
    file = open(error,'a')
    file.write(log)
    file.close()



def Adjust(t0, wO, scale, portI, portE, inc, out, name, reactor, error):
    """adjust the reactor weight by pumping influent/effluent (i.e. charge reactor)"""
    #connect to trinamic board and read current scale mass
    doI = Connect(portI, reactor, error)
    doE = Connect(portE, reactor, error)
    w0 = Scale(scale, reactor, error)
    dw = 0
    calflow = 2e-4
    c = 0
    Writ(t0, scale, 'C', 0, name, wO, reactor, error)
    
    #run the pumps until the target mass is achieved    
    while abs(wO-dw) > 0.1:
    	#run influent     
        if dw > wO:
            vel = abs(int((dw-wO)/calflow))
            if vel > 2000:
                vel = 2000
            doE.rotate(out,vel)
            time.sleep(0.5)
            doE.stop(out)
        else:
            vel = abs(int((wO-dw)/calflow))            
            if vel > 2000:
                vel = 2000
            doI.rotate(inc,vel)
            time.sleep(0.5)
            doI.stop(inc)
        dw = Scale(scale, reactor, error) - w0
        c = c+1
        if c%20 == 0:
            Writ(t0, scale , 'C', 0, name, wO+w0, reactor, error)

            
            
def Wait(future, stage, error, reactor, t0, scale, name, Ob):
    Tw = time.time()
    if future-Tw > 30:
        print('Time left for reactor: ', reactor)
        print(round((future-Tw)/60,1),'min')
        Reac = pd.read_excel('Reactors.xlsx',index_col=0)
        Reac[reactor]['Wait (min)'] = (future-Tw)/60
        Reac.to_excel('Reactors.xlsx')
        time.sleep(30)
        system('clear')
        Writ(t0, scale, stage, 0, name, Ob, reactor, error)
        Wait(future, stage, error, reactor, t0, scale, name, Ob)
        return 0
    elif future-Tw < 0:
        WritEr('Negative waiting time ('+ str(future-Tw)+')',error)
        return 0
    else:
        time.sleep(future-Tw)
        return 0


    
def Connect(port, reactor, error):
    """connect to the Trinamic controller to allow control of pumps"""
    board = '/dev/Trinamic' + port
    argu = ['--port', board]
    while True:
        try:
            con = ConnectionManager(argList=argu)
            do = con.connect()
            return do
        except:
            print('Error: ' + board + ' disconnected')
            time.sleep(30)
            Reac = pd.read_excel('Reactors.xlsx', index_col=0)
            port = str(Reac[reactor]['Port'])
            WritEr('Port '+ str(port)+ ' disconnected', error)    
         
    
                 
def InfC(t0, cycle, stage, veli, hW, Ob, influent, port, spectime, reactor, scale, error, name, tsleep):
    """run the influent pump until the target reactor mass is achieved"""
    do = Connect(port, reactor, error)
    dm = 10
    startw = Scale(scale, reactor, error)
    ctime0 = time.time()
    ctimeM = 0
    if cycle == 1:
        Ref = hW
    elif cycle == 2:
        Ref = Ob
    print('Influent:', reactor)
    Writ(t0, scale, stage, veli, name, Ob, reactor, error)
    while dm > 0:
        do.rotate(influent, veli)
        time.sleep(tsleep)
        do.stop(influent)
        curw = Scale(scale, reactor, error)
        delw = curw - startw
        dm = Ref-curw
        ctime = time.time() - ctime0
        if ctime-ctimeM > 30:
            ctimeM = ctime
            Writ(t0, scale, stage, veli, name, Ob, reactor, error)
        #interrupt the program if the reactor weight is not changing during pumping
        if ctime > 240 and delw < 1:
            print(ctime)
            while True:
                try:
                    print(str(datetime.datetime.now()))
                    WritEr('Reactor stoped because of influent (scale response)',error)
                    fix = str(input('Fixed? (y)'))                   
                    if fix == 'y':
                        ctime0 = time.time()
                        break
                except:
                    print('Error, wait 60 s')
                    time.sleep(60)
        #in rare circumstances, stop the pump before it overheats
        if ctime > 600:
            while True:
                try:
                    print(str(datetime.datetime.now()))
                    WritEr('Reactor stoped because of influent (pump runtime)',error)
                    fix = str(input('Fixed? (y)'))                   
                    if fix == 'y':
                        ctime0 = time.time()
                        break
                except:
                    print('Error, wait 60 s')
                    time.sleep(60)
    do.rotate(influent,-veli)
    time.sleep(tsleep)
    do.stop(influent)
    system('clear')
    time.sleep(1)
    Writ(t0, scale, stage, veli, name, Ob, reactor, error)
    return
    
    
def EffC(t0, cycle, stage, vele, lW, Ob, efluent, port, spectime, reactor, scale, error, name, tsleep):
    do = Connect(port, reactor, error)
    dm = 10
    ctime0 = time.time()
    ctimeM = 0
    startw = Scale(scale, reactor, error)
    if cycle == 1:
        Ref=Ob
    elif cycle ==2:
        Ref=lW
    print('Effluent:',reactor)
    Writ(t0, scale, stage, vele, name, Ob, reactor, error)
    while dm > -0.2:
        do.rotate(efluent, vele)
        time.sleep(tsleep)
        do.stop(efluent)
        time.sleep(tsleep)
        curw = Scale(scale, reactor, error)
        delw = curw - startw
        dm = curw - Ref
        ctime = time.time()-ctime0
        if (ctime-ctimeM) > 30:
            ctimeM = ctime
            Writ(t0, scale, stage, vele, name, Ob, reactor, error)
        #interrupt the program if the scale is not responsive to pumping
        if ctime > 300 and delw > -0.5:
            while True:
                try:
                    print(str(datetime.datetime.now()))
                    WritEr('Reactor stoped because of effluent (scale response)',error)
                    fix = str(input('Fixed ? (y)'))                   
                    if fix == 'y':
                        ctime0 = time.time()
                        break
                except:
                    print('Error, wait 60 s')
                    time.sleep(60)
        if ctime > 1500:
        #in rare circumstances, stop the pump before it overheats
            while True:
                try:
                    print(str(datetime.datetime.now()))
                    WritEr('Reactor stoped because of effluent (pump runtime)',error)
                    fix = str(input('Fixed ? (y)'))                   
                    if fix == 'y':
                        ctime0 = time.time()
                        break
                except:
                    print('Error, wait 60 s')
                    time.sleep(60)
    Etime0 = time.time()
    Etime = time.time()
    Et = Etime-Etime0
    while dm < -0.1 and Et < 30:
        do.rotate(efluent,-vele)
        time.sleep(tsleep)
        do.stop(efluent)
        time.sleep(tsleep*5)
        dm = Scale(scale,reactor,error)-Ref
        ctime = time.time()-ctime0
        Etime = time.time()
        Et = Etime-Etime0
        print(Et)                
    do.stop(efluent)
    system('clear')
    time.sleep(1)
    Writ(t0, scale, stage, vele, name, Ob, reactor, error)
    
    
    
def Stop(portI, portE, Minfluent, Mefluent, reactor, error):
    "stop both of the pumps connected to the reactor"
    doI = Connect(portI, reactor, error)
    doE = Connect(portE, reactor, error)
    doI.stop(Minfluent)
    doE.stop(Mefluent) 
    
    
    
def Control(re, reactor, loc):
    t0 = time.time()
    scale = "Scale" + str(re + 1)
    name = loc +'/data.csv'
    error = loc +'/error.csv'  
    
    while True:
        try:
            #read all the values from the reactor.xlsx file
            Reac = pd.read_excel('Reactors.xlsx',index_col=0)
            startt = time.time()            
            portI = str(Reac[reactor]['PortI'])
            portE = str(Reac[reactor]['PortE'])            
            veli = int(Reac[reactor]['SpeedInf'])
            vele = int(Reac[reactor]['SpeedEff'])
            Minfluent = int(Reac[reactor]['Minfluent'])
            Mefluent = int(Reac[reactor]['Meffluent'])
            m = float(Reac[reactor]['Weigth (g)'])
            charge = float(Reac[reactor]['Charge (g)'])
            D = float(Reac[reactor]['D (1/h)'])/60
            cycle = Reac[reactor]['Cycle (min)']
            tsleep = Reac[reactor]['tsleep (s)']          
            start = int(Reac[reactor]['Start'])
            move = int(Reac[reactor]['Move'])        
            wart = Reac[reactor]['Wait (min)']
            stage = int(Reac[reactor]['Stage'])  

            #charge reactor by the amount specified in the excel file
            if charge != 0:
                Stop(portI=portI,portE=portE,Minfluent=Minfluent,Mefluent=Mefluent,reactor=reactor,error=error)            
                Adjust(t0, charge, scale, portI, portE, Minfluent, Mefluent, name, reactor, error)
                Reac[reactor]['Charge (g)']=0
                Reac.to_excel('Reactors.xlsx')
                
            # reset the scale setpoint if it was moved or restarted, else use value from excel
            if start == 1 or move == 1:
                print('Moved')
                Ob = Scale(scale,reactor,error)
                Reac[reactor]['SetPoint'] = Ob
                Reac[reactor]['Start'] = 0
                Reac[reactor]['Move'] = 0
                Reac.to_excel('Reactors.xlsx')
            else:
                Ob = Reac[reactor]['SetPoint']
                
            #wait the amount of time specified in the excel file
            if wart != 0:         
                Wait(wart*60+time.time(), stage, error, reactor, t0, scale, name, Ob)
                Reac[reactor]['Wait (min)']=0
                if stage == 6 or stage == 3:
                    stage = stage+1
                Reac.to_excel('Reactors.xlsx')
                
            #calculate the mass to dose into the reactors
            flow = m*D #g/hr
            inout = flow*cycle #g/cycle
            dw = inout/2
            hW = Ob + dw #high weight to reach
            lW = Ob - dw #low weight to reach
            
            #define pause times in seconds
            Tpause = 60*cycle #seconds
            spectime = Tpause/4
            
            #stage 1: influent 1
            if stage == 1:         
                cycle = 1
                print('Stage:',stage)
                Stop(portI, portE, Minfluent, Mefluent, reactor, error)
                InfC(t0, cycle, stage, veli, hW, Ob, Minfluent, portI, spectime, reactor, scale, error, name, tsleep)
                Wait(120+time.time(), stage, error, reactor, t0, scale, name, Ob) 
                stage = 2
                Reac[reactor]['Stage'] = stage
                Reac[reactor]['Startt'] = startt                
                Reac[reactor].to_excel('Reactors.xlsx')
                
            #stage 2: effluent 1
            elif stage == 2:
                print('Stage:',stage)   
                cycle = 1
                Stop(portI, portE, Minfluent, Mefluent, reactor, error)
                EffC(t0, cycle, stage, vele, lW, Ob, Mefluent, portE, spectime, reactor, scale, error, name, tsleep)
                stage = 3
                Reac[reactor]['Stage'] = stage             
                Reac.to_excel('Reactors.xlsx')
                
            #stage 3: wait time in middle of cycle
            elif stage == 3:
                print('Stage:',stage)    
                Writ(t0,scale,stage,0,name,Ob,reactor,error)                
                startt = Reac[reactor]['Startt']             
                end0 = time.time() - startt
                wait = (Tpause-end0)/5                
                Wait(wait+time.time(), stage, error, reactor, t0, scale, name, Ob)
                Writ(t0, scale, stage, 0, name, Ob, reactor, error)   
                stage = 4
                Reac[reactor]['Stage'] = stage
                Reac.to_excel('Reactors.xlsx')
                
            #stage 4: effluent 2
            elif stage == 4:
                print('Stage:',stage)   
                cycle = 2
                Stop(portI, portE, Minfluent, Mefluent, reactor, error)                
                EffC(t0, cycle, stage, vele, lW, Ob, Mefluent, portE, spectime, reactor, scale, error, name, tsleep)           
                Wait(120+time.time(), stage, error, reactor, t0, scale, name, Ob)
                stage = 5
                Reac[reactor]['Stage'] = stage
                Reac.to_excel('Reactors.xlsx')
                
            #stage 5: influent 2
            elif stage == 5:
                print('Stage:',stage)    
                cycle = 2
                Stop(portI, portE, Minfluent, Mefluent, reactor, error)               
                InfC(t0, cycle, stage, veli, hW, Ob, Minfluent, portI, spectime, reactor, scale, error, name, tsleep)
                stage = 6
                Reac[reactor]['Stage'] = stage
                Reac.to_excel('Reactors.xlsx')

            #stage 6: wait until next pump cycle               
            elif stage == 6:
                print('Stage:',stage)     
                Writ(t0, scale, stage, 0, name, Ob, reactor, error)  
                startt = Reac[reactor]['Startt']                              
                end = time.time() - startt
                wait = Tpause - end                
                Wait(wait+time.time(), stage, error, reactor, t0, scale, name, Ob)
                Reac=pd.read_excel('Reactors.xlsx',index_col=0)
                Writ(t0, scale, stage, 0, name, Ob, reactor, error)
                stage=1
                Reac[reactor]['Stage']=stage
                Reac.to_excel('Reactors.xlsx') 

            #check if instructions were given to stop the program                 
            Reac=pd.read_excel('Reactors.xlsx',index_col=0)
            portI = str(Reac[reactor]['PortI'])
            portE = str(Reac[reactor]['PortE'])            
            stop=Reac[reactor]['Stop']
            if stop == 1:
                Stop(portI, portE, Minfluent, Mefluent, reactor, error)            
                if input('Are you sure?') == 1:
                    return 0
        except:
            print('Unknown Error')
            Stop(portI, portE, Minfluent, Mefluent, reactor, error)            
            time.sleep(60)
            WritEr('Unknown error', error)


def Main(re):
    """initiate the main control loop"""
    re = int(re) - int(1)    
    Reac = pd.read_excel('Reactors.xlsx', index_col=0)
    Rname = str(Reac.iloc[:,re].name)
    print('Selected reactor: ' + Rname)
    Reac.to_excel('Reactors.xlsx', columns=[Rname])
    here = getcwd()
    Control(re, Rname, here)      
 
    
Main(input())

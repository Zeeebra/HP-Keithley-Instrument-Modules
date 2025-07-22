"""
File: HP4155.py
Author: Zhi Li.
Creation Date: 03/25/2023
Modified Date (by): 
Version: 0.1
Description: A module to control HP4155B to run sweeping and sampling test.
"""


import pyvisa
import time
import matplotlib.pyplot as plt
import datetime

class HP4155B:

    def __init__(self):
        try:
            rm = pyvisa.ResourceManager(r'C:\\Windows\\system32\\visa32.dll')
            rm.list_resources()
            # GPIB0::4::INSTR for HP4155B
            # GPIB0::17::INSTR for HP4156C
            self.inst = rm.open_resource('GPIB0::4::INSTR')
            self.inst.read_termination = '\n'
            print(self.inst.query('*IDN?'))
            self.inst.timeout = 6000
            self.inst.write('*RST') ## reset
            time.sleep(.1)
            self.inst.write('US') ## set to FLEX mode
        except:
            print("Error connecting to HP4155B.")
    
    def IVcurve_glassCoupons(self,start,stop,step,myHold,myDelay,myInt):
        
        nPts = ((stop - start) / step) + 1

        SMU1, SMU2, SMU3, SMU4 = 1, 2, 3, 4
        VSU1, VSU2 = 21, 22

        # Set control mode of HP4156
        self.inst.write('*RST') ## reset
        self.inst.write('US') ### flex mode

        self.inst.write('CM 0') ### Disable auto-calibration
        self.inst.write('FMT 2,1') ### Set data output format to ASCII without header, with sweep source data
        # self.inst.write('TSC 1') ### Enable the time stamp output, not available for HP4155B
        self.inst.write('Fl 0') ### Set filters off
        self.inst.write(f'CN {SMU1}, {SMU2}, {SMU3}, {SMU4}, {VSU1}') ### Enable SMU1-4 and VSU1


        # Measurement settings: sweep measurement
        self.inst.write(f'MM 2,{SMU1},{SMU2},{SMU3},{SMU4}') ### Set measurement mode to 2, staircase sweep for SMU1-4
        self.inst.write('WT ' + str(myHold) + ',' + str(myDelay)) ### Set hold time and delay time in seconds
        self.inst.write('SIT 1,' + str(myInt)) ### Set integration time in seconds, 80e-6 to 10e-3
        self.inst.write('SLI 1') ### Set integration time to Short
        self.inst.write('RI ' + str(SMU1) + ',16,2') ### Set current measurement range to AUTO ranging (100 uA limited auto ranging)
        self.inst.write('RI ' + str(SMU2) + ',16,2') ### Set current measurement range to AUTO ranging (100 uA limited auto ranging)
        self.inst.write('RI ' + str(SMU3) + ',16,2') ### Set current measurement range to AUTO ranging (100 uA limited auto ranging)
        self.inst.write('RI ' + str(SMU4) + ',16,2') ### Set current measurement range to AUTO ranging (100 uA limited auto ranging)

        # Source setting: single stair, auto range, start, stop, # of steps, compliance
        self.inst.write('WV ' + str(VSU1) + ',1,0,' + str(start) + ',' + str(stop) + ',' + str(nPts))

        ## Execute the test ##
        ##########################################################################################################################
        self.inst.write('WM 1') ### Turn off auto abort, equavalent to "CONTINUE AT ANY" on EasyExpert
        self.inst.write('TSR') ### Clear the timer count

        # Execute measurement
        self.inst.write('XE') #
        self.inst.write('*OPC?')
        while self.inst.stb != 24:
            time.sleep(0.2)

        self.inst.write('RMD? 0')
        clearone = self.inst.read()
        myData = self.inst.read_ascii_values(separator = ',')
        ##########################################################################################################################

        myV = myData[4::5]
        myI1 = myData[0::5]
        myI2 = myData[1::5]
        myI3 = myData[2::5]
        myI4 = myData[3::5]
        nPoint=len(myV)
        print('Forward I-V sweep done, ' + str(nPoint) + 'points')
        return [myV,myI1,myI2,myI3,myI4]
    
    def Sampling_glassCoupons(self, hold,interval,points,ptstoavg,myInt):

        SMU1, SMU2, SMU3, SMU4 = 1, 2, 3, 4
        VSU1, VSU2 = 21, 22

        Vtop = 0
        Vbot = 2

        # Set control mode of HP4156
        self.inst.write('*RST') ## reset
        self.inst.write('US') ### flex mode

        self.inst.write('CM 0') ### Disable auto-calibration
        self.inst.write('FMT 2,1') ### Set data output format to ASCII without header, with sweep source data
        # inst.write('TSC 1') ### Enable the time stamp output, not available for HP4155B
        self.inst.write('Fl 0') ### Set filters off
        self.inst.write(f'CN {SMU1},{SMU2},{SMU3},{SMU4},{VSU1}') ### Enable SMU1-4 and VSU1

        # Measurement settings: sampling measurement
        self.inst.write('MT ' + str(hold) + ',' + str(interval) + ',' + str(points))  ## configure sampling measurement (before MM 10 !!!)
        self.inst.write(f'MM 10,{SMU1},{SMU2},{SMU3},{SMU4}') ### Set measurement mode to 10, sampling measurement mode
        self.inst.write('SIT 1,' + str(myInt)) ### Set integration time in seconds, 80e-6 to 10e-3
        self.inst.write('SLI 1') ### Set integration time to Short
        self.inst.write('AV ' + str(ptstoavg)) ### Set number of samples to average for one data point

        self.inst.write('RI ' + str(SMU1) + ',16,2') ### Set current measurement range to AUTO ranging (100 uA limited auto ranging)
        self.inst.write('RI ' + str(SMU2) + ',16,2') ### Set current measurement range to AUTO ranging (100 uA limited auto ranging)
        self.inst.write('RI ' + str(SMU3) + ',16,2') ### Set current measurement range to AUTO ranging (100 uA limited auto ranging)
        self.inst.write('RI ' + str(SMU4) + ',16,2') ### Set current measurement range to AUTO ranging (100 uA limited auto ranging)

        # Source settings: spots measurement
        self.inst.write(f'MV {VSU1},12,{Vbot},{Vbot}') ### for VSU (bot), MV chnum,range,base,bias[,Icomp]

        ## Execute the test ##
        ##########################################################################################################################
        self.inst.write('WM 1') ### Turn off auto abort, equavalent to "CONTINUE AT ANY" on EasyExpert
        self.inst.write('TSR') ### Clear the timer count

        # Execute measurement
        self.inst.write('XE') #
        self.inst.write('*OPC?')
        while self.inst.stb != 24:
            time.sleep(0.2)

        self.inst.write('RMD? 0')
        clearone = self.inst.read()
        myData = self.inst.read_ascii_values(separator = ',') 
        ##########################################################################################################################

        myTime = myData[::5]
        myTime = [float(x)*interval for x in myTime]
        myI1 = myData[1::5]
        myI2 = myData[2::5]
        myI3 = myData[3::5]
        myI4 = myData[4::5]

        return [myTime,myI1,myI2,myI3,myI4]
    
    def IVcurve_probestation(self,start,stop,step,myHold,myDelay,myInt):
        
        nPts = ((stop - start) / step) + 1

        SMU1, SMU2, SMU3, SMU4 = 1, 2, 3, 4
        VSU1, VSU2 = 21, 22

        # Set control mode of HP4156
        self.inst.write('*RST') ## reset
        self.inst.write('US') ### flex mode

        self.inst.write('CM 0') ### Disable auto-calibration
        self.inst.write('FMT 2,1') ### Set data output format to ASCII without header, with sweep source data
        # self.inst.write('TSC 1') ### Enable the time stamp output, not available for HP4155B
        self.inst.write('Fl 0') ### Set filters off
        self.inst.write(f'CN {SMU1}, {SMU2}') ### Enable SMU1 and SMU2


        # Measurement settings: sweep measurement
        self.inst.write(f'MM 2,{SMU1},{SMU2}') ### Set measurement mode to 2, staircase sweep for SMU1 and SMU2
        self.inst.write('WT ' + str(myHold) + ',' + str(myDelay)) ### Set hold time and delay time in seconds
        self.inst.write('SIT 1,' + str(myInt)) ### Set integration time in seconds, 80e-6 to 10e-3
        self.inst.write('SLI 1') ### Set integration time to Short
        self.inst.write('RI ' + str(SMU1) + ',11,0') ### Set current measurement range to AUTO ranging (100 uA limited auto ranging)
        self.inst.write('RI ' + str(SMU2) + ',11,0') ### Set current measurement range to AUTO ranging (100 uA limited auto ranging)

        # Source setting: single stair, auto range, start, stop, # of steps, compliance
        self.inst.write('WV ' + str(SMU2) + ',1,0,' + str(start) + ',' + str(stop) + ',' + str(nPts))

        ## Execute the test ##
        ##########################################################################################################################
        self.inst.write('WM 1') ### Turn off auto abort, equavalent to "CONTINUE AT ANY" on EasyExpert
        self.inst.write('TSR') ### Clear the timer count

        # Execute measurement
        self.inst.write('XE') #
        self.inst.write('*OPC?')
        while self.inst.stb != 24:
            time.sleep(0.2)

        self.inst.write('RMD? 0')
        clearone = self.inst.read()
        myData = self.inst.read_ascii_values(separator = ',')
        ##########################################################################################################################

        myV = myData[2::3]
        myI1 = myData[0::3]
        myI2 = myData[1::3]
        nPoint=len(myV)
        print('Forward I-V sweep done, ' + str(nPoint) + 'points')
        return [myV,myI1,myI2]
    


if __name__ == "__main__":
    start = -1 # V
    stop = 3 # V
    step = 0.05 # V
    myInt = .01 # second, previous default 0.001 sec
    myHold = 0
    myDelay = 0

    HP = HP4155B() # Instantiate HP4156 class and connect to HP4156
    [myV,myI1, myI2] = HP.IVcurve_probestation(start,stop,step,myHold,myDelay,myInt)
    myIlst = [myI1, myI2]

    print(min(myI1))

    ## Bias vs. current
    colorlst = ['black', 'red', 'blue', 'green']
    fig = plt.figure(figsize = [12, 8])
    ax = fig.add_subplot(111)

    ax.scatter(myV, list(map(lambda x: (-1)*x, myI1)), color='red', s = 5, marker = 'o', label = f'SMU1')
    ax.plot(myV, list(map(lambda x: (-1)*x, myI1)), color='red')
    ax.set_title(f'Probe station IV')
    ax.set_xlabel('Bias (V)')
    ax.set_ylabel('Current (A)')
    ax.legend()
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    plt.show()
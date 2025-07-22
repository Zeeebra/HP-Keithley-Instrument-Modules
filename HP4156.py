"""
File: HP4156.py
Author: Zhi Li.
Creation Date: 11/13/2023
Modified Date (by): 07/23/2024
Version: 0.1
Description: A module to control HP4156C to run sweeping and sampling test. 
07/15 editting changes current range to "RI 16, 0" from "RI 16, 2" and disable SMU1-4 and VSU1 after finishing the experiment
07/23 editting changes sweeping directions to both and make current measurement range and range type to input parameters.
"""


import pyvisa
import time
import matplotlib.pyplot as plt
import datetime

class HP4156C:

    def __init__(self):
        try:
            rm = pyvisa.ResourceManager(r'C:\\Windows\\system32\\visa32.dll')
            rm.list_resources()
            self.inst = rm.open_resource('GPIB0::17::INSTR')
            self.inst.read_termination = '\n'
            print(self.inst.query('*IDN?'))
            self.inst.timeout = 6000
            self.inst.write('*RST') ## reset
            time.sleep(.1)
            self.inst.write('US') ## set to FLEX mode
        except:
            print("Error connecting to HP4156C.")
    
    def IVcurve_glassCoupons(self,start,stop,step,myHold,myDelay,myInt,Irange_value_code=16, Irange_type_code=0):
        
        nPts = (abs(stop - start) / step) + 1

        SMU1, SMU2, SMU3, SMU4 = 1, 2, 3, 4
        VSU1, VSU2 = 21, 22

        # Set control mode of HP4156
        self.inst.write('*RST') ## reset
        self.inst.write('US') ### flex mode

        self.inst.write('CM 0') ### Disable auto-calibration
        self.inst.write('FMT 2,1') ### Set data output format to ASCII without header, with sweep source data
        self.inst.write('TSC 1') ### Enable the time stamp output
        self.inst.write('Fl 0') ### Set filters off
        self.inst.write(f'CN {SMU1}, {SMU2}, {SMU3}, {SMU4}, {VSU1}') ### Enable SMU1-4 and VSU1


        # Measurement settings: sweep measurement
        self.inst.write(f'MM 2,{SMU1},{SMU2},{SMU3},{SMU4}') ### Set measurement mode to 2, staircase sweep for SMU1-4
        self.inst.write('WT ' + str(myHold) + ',' + str(myDelay)) ### Set hold time and delay time in seconds
        self.inst.write('SIT 1,' + str(myInt)) ### Set integration time in seconds, 80e-6 to 10e-3
        self.inst.write('SLI 1') ### Set integration time to Short
        self.inst.write(f'RI {SMU1},{Irange_value_code},{Irange_type_code}') ### Set current measurement range and range type
        self.inst.write(f'RI {SMU2},{Irange_value_code},{Irange_type_code}') ### Set current measurement range and range type
        self.inst.write(f'RI {SMU3},{Irange_value_code},{Irange_type_code}') ### Set current measurement range and range type
        self.inst.write(f'RI {SMU4},{Irange_value_code},{Irange_type_code}') ### Set current measurement range and range type

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

        self.inst.write(f'CL {SMU1}, {SMU2}, {SMU3}, {SMU4}, {VSU1}') ### Disable SMU1-4 and VSU1

        myV = myData[8::9]
        myTime1 = myData[::9]
        myTime1 = [float(x)*1e-4 for x in myTime1]
        myI1 = myData[1::9]
        myTime2 = myData[2::9]
        myTime2 = [float(x)*1e-4 for x in myTime2]
        myI2 = myData[3::9]
        myTime3 = myData[4::9]
        myTime3 = [float(x)*1e-4 for x in myTime3]
        myI3 = myData[5::9]
        myTime4 = myData[6::9]
        myTime4 = [float(x)*1e-4 for x in myTime4]
        myI4 = myData[7::9]
        nPoint=len(myV)
        print('Forward I-V sweep done, ' + str(nPoint) + 'points')
        return [myV,myI1,myTime1,myI2,myTime2,myI3,myTime3,myI4,myTime4]

    def Sampling_glassCoupons(self,hold,interval,points,ptstoavg,myInt):

        SMU1, SMU2, SMU3, SMU4 = 1, 2, 3, 4
        VSU1, VSU2 = 21, 22

        Vtop = 0
        Vbot = 2

        # Set control mode of HP4156
        self.inst.write('*RST') ## reset
        self.inst.write('US') ### flex mode

        self.inst.write('CM 0') ### Disable auto-calibration
        self.inst.write('FMT 2,1') ### Set data output format to ASCII without header, with sweep source data
        self.inst.write('TSC 1') ### Enable the time stamp output
        self.inst.write('Fl 0') ### Set filters off
        self.inst.write(f'CN {SMU1},{SMU2},{SMU3},{SMU4},{VSU1}') ### Enable SMU1-4 and VSU1

        # Measurement settings: sampling measurement
        self.inst.write('MT ' + str(hold) + ',' + str(interval) + ',' + str(points))  ## configure sampling measurement (before MM 10 !!!)
        self.inst.write(f'MM 10,{SMU1},{SMU2},{SMU3},{SMU4}') ### Set measurement mode to 10, sampling measurement mode
        self.inst.write('SIT 1,' + str(myInt)) ### Set integration time in seconds, 80e-6 to 10e-3
        self.inst.write('SLI 1') ### Set integration time to Short
        self.inst.write('AV ' + str(ptstoavg)) ### Set number of samples to average for one data point

        self.inst.write('RI ' + str(SMU1) + ',16,0') ### Set current measurement range to AUTO ranging (100 uA limited auto ranging)
        self.inst.write('RI ' + str(SMU2) + ',16,0') ### Set current measurement range to AUTO ranging (100 uA limited auto ranging)
        self.inst.write('RI ' + str(SMU3) + ',16,0') ### Set current measurement range to AUTO ranging (100 uA limited auto ranging)
        self.inst.write('RI ' + str(SMU4) + ',16,0') ### Set current measurement range to AUTO ranging (100 uA limited auto ranging)

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
        self.inst.write(f'CL {SMU1}, {SMU2}, {SMU3}, {SMU4}, {VSU1}') ### Disable SMU1-4 and VSU1

        myIndex = myData[::9]

        myTime1 = myData[1::9]
        myTime1 = [float(x)*1e-4 for x in myTime1]
        myI1 = myData[2::9]

        myTime2 = myData[3::9]
        myTime2 = [float(x)*1e-4 for x in myTime2]
        myI2 = myData[4::9]

        myTime3 = myData[5::9]
        myTime3 = [float(x)*1e-4 for x in myTime3]
        myI3 = myData[6::9]

        myTime4 = myData[7::9]
        myTime4 = [float(x)*1e-4 for x in myTime4]
        myI4 = myData[8::9]
        nPoint=len(myIndex)

        #print('Sampling done, ' + str(nPoint) + 'points')
        return [myIndex,myI1,myTime1,myI2,myTime2,myI3,myTime3,myI4,myTime4]


if __name__ == "__main__":
    hold = 0
    interval = 1 # secondc, sampling interval
    myInt = .01 # second, previous default 0.001 sec
    points = 10 # number of data points
    ptstoavg = 3 # number of measurements to average per point.

    HP = HP4156C() # Instantiate HP4156 class and connect to HP4156
    [myIndex,myI1,myTime1,myI2,myTime2,myI3,myTime3,myI4,myTime4] = HP.Sampling_glassCoupons(hold,interval,points,ptstoavg,myInt)
    myIlst = [myI1, myI2, myI3, myI4]
    myTimelst = [myTime1, myTime2, myTime3, myTime4]

    ## Time vs. Current plots
    colorlst = ['black', 'red', 'blue', 'green']
    fig = plt.figure(figsize = [12, 8])
    ax = fig.add_subplot(111)
    for i in range(4):
        ax.scatter(myTimelst[i], myIlst[i], color=colorlst[i], s = 5, marker = 'o', label = f'Device #{i+1}')
        ax.set_title(f'Sampling at light level_0 mA')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Current (A)')
    ax.legend()
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    plt.show()
"""
File: B1500.py
Author: Zhi Li.
Creation Date: 08/02/2024
Modified Date (by): 
Version: 0.1
Description: A module to control B1500 to run sweeping and sampling test.
"""


import pyvisa
import time
import matplotlib.pyplot as plt
import datetime

class B1500:

    def __init__(self):
        try:
            rm = pyvisa.ResourceManager(r'C:\\Windows\\system32\\visa32.dll')
            rm.list_resources()
            self.inst = rm.open_resource('GPIB1::2::INSTR') ## address for T200 B1500
            self.inst.read_termination = '\n'
            print(self.inst.query('*IDN?'))
            self.inst.timeout = 6000
            self.inst.write('*RST') ## reset the tester
            time.sleep(.1)
            self.inst.write('US') ## set to FLEX mode
        except:
            print("Error connecting to B1500.")

    def IVcurve(self,start,stop,step,myHold,myDelay,myInt_PLC,Irange_value_code=16, Irange_type_code=0):
        start = -0.5
        stop = 1
        step = 0.02
        Irange_value_code = 16
        Irange_type_code = 0
        myHold = 0
        myDelay = 0
        myInt_PLC = 1 # integer, 1-100, 1 means 1 period of power line, approximate 1/60HZ = 17ms
        nPts = int((abs(stop - start) / step) + 1)
        SMU1, SMU2, SMU3, SMU4 = 1, 2, 3, 4

        # Set control mode of B1500
        self.inst.write('*RST') ## reset
        self.inst.write('US') ### flex mode

        self.inst.write('CM 0') ### Disable auto-calibration
        self.inst.write('FMT 2,1') ### Set data output format to ASCII without header, with sweep source data
        self.inst.write('TSC 1') ### Enable the time stamp output
        self.inst.write('Fl 0') ### Set filters off
        self.inst.write(f'CN {SMU1}, {SMU2}') ### Enable SMU1-4 and VSU1


        # Measurement settings: sweep measurement
        self.inst.write(f'MM 2,{SMU1}') ### Set measurement mode to 2, staircase sweep for SMU1-4
        self.inst.write('WT ' + str(myHold) + ',' + str(myDelay)) ### Set hold time and delay time in seconds
        ### 0: high speed A/D converter, 1: high resolution A/D converter, 2: High-speed ADC for pulsed-measurement
        self.inst.write(f'AAD {SMU1}, 1')
        ### AIT type,mode[,N], for mode, use 0: Auto mode. Initial setting, 1: Manual mode, 2: Power line cycle (PLC) mode, 3: Measurement time mode. Not available for the high-resolution ADC.
        self.inst.write(f'AIT 1, 2, {myInt_PLC}')
        self.inst.write(f'RI {SMU1},{Irange_value_code},{Irange_type_code}') ### Set current measurement range and range type

        # Source setting: single stair, auto range, start, stop, # of steps, compliance
        self.inst.write('WV ' + str(SMU2) + ',1,0,' + str(start) + ',' + str(stop) + ',' + str(nPts) + ',' + '0.0001')

        ## Execute the test ##
        ##########################################################################################################################
        self.inst.write('TSR') ### Clear the timer count

        # Execute measurement
        self.inst.write('XE') #
        self.inst.write('*OPC?')

        # Check if experiment finished or not. When it is finished, read the data.
        while self.inst.stb != 49:
            time.sleep(0.2)
        clearone = self.inst.read()
        myData = self.inst.read_ascii_values()
        ##########################################################################################################################

        self.inst.write(f'CL {SMU1}, {SMU2}') ### Disable SMUs

        myV = myData[2::3]
        myTime = myData[0::3]
        myI = myData[1::3]
        nPoint=len(myV)

        print('Forward I-V sweep done, ' + str(nPoint) + 'points')
        return [myV,myI]
    

if __name__ == "__main__":
    start = -0.5
    stop = 1
    step = 0.02
    Irange_value_code = 16
    Irange_type_code = 0
    myHold = 0
    myDelay = 0
    myInt_PLC = 1

    B1500 = B1500()
    [myV, myI] = B1500.IVcurve(start,stop,step,myHold,myDelay,myInt_PLC,Irange_value_code, Irange_type_code)

    ## Bias vs. Current plots
    fig = plt.figure(figsize = [12, 8])
    ax = fig.add_subplot(111)
    ax.scatter(myV, list(map(lambda x: (-1)*x, myI)), color='red', s = 5, marker = 'o', label = f'SMU1')
    # ax.plot(myV, list(map(lambda x: (-1)*x, myI)), color='red')
    ax.set_title(f'IV curve')
    ax.set_xlabel('Bias (V)')
    ax.set_ylabel('Current (A)')
    ax.legend()
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    plt.show()
"""
File: Keithley2450.py
Author: Zhi Li, STMicroelectronics Inc.
Creation Date: 07/18/2024
Modified Date (by): 
Version: 0.1
Description: A module to control Keithley2450 to run sweeping test.
"""


import pyvisa
import time
import matplotlib.pyplot as plt
import numpy as np

class Keithley2450:

    def __init__(self):
        try:
            rm = pyvisa.ResourceManager(r'C:\\Windows\\system32\\visa32.dll')
            rm.list_resources()
            self.inst = rm.open_resource('GPIB1::18::INSTR')
            print(self.inst.query('*IDN?'))
            self.inst.timeout = 6000
            self.inst.write('*LANG SCPI')
            self.inst.read_termination = '\n'
            self.inst.write_termination = '\n'
            self.inst.write('*RST') ## reset
            self.inst.write(':TRAC:CLEAR')
            self.inst.write(':ROUTe:TERMinals REAR')
            time.sleep(.1)
        except:
            print("Error connecting to Keithley2450.")

    def IVcurve(self, start, stop, step):
        nPts = int((stop-start)/step + 1)
        V_lst = list(np.linspace(start,stop,nPts))
        I_lst = []
        self.inst.write('OUTP ON')
        for v in V_lst:
            self.inst.write(f':SOUR:VOLT:LEV {v}') # Keithley set bias as v
            self.inst.write(':READ?') # Keithley read current
            I_lst.append(float(self.inst.read()))
        self.inst.write('OUTP OFF')
        return [V_lst, I_lst]
    

if __name__ == "__main__":

    start = 0 # V
    stop = 1 # V
    step = 0.02 # V
    Keithley = Keithley2450()
    [bias, current] = Keithley.IVcurve(start,stop,step)
    fig = plt.figure(figsize = [12,8])
    ax = fig.add_subplot(111)
    ax.scatter(bias, current, color = 'red')
    plt.show()
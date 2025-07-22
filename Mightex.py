"""
File: Mightex.py
Author: Zhi Li
Creation Date: 11/13/2023
Modified Date (by):
Version: 0.1
Description: A module to control Mightex LED controller. Current version has full accessibility on normal mode of LED operation.
"""

from serial_device2 import SerialDevice, ReadError

class MightexLED:

    '''
    This is a class for MightexLED. It basically wrapped up the "SerialDevice" moduel from serial library.
    It is required to define the atrribute port ("COM?", find it in device management of PC) in use to instantiate the class, because it is usually not recornized for PC.
    For other systems:
        Linux: port='/dev/ttyUSB0'
        Mac OS: port='/dev/tty.usbmodem262471'
    When it is initiated, attribute "device" is an instance of SerialDevice. Most methods in this class will use "device".
    
    '''

    def __init__(self,port,channel):
        self.port = port
        self.device = SerialDevice(port = self.port)
        self.channel = channel

    def port(self):
        '''
        Retrieve port number of connected LED
        '''
        return self.device.port
    
    def request_gen(self,*args):
        '''
        This method is to generate formated cmd to control LED. For example if *args = 'DEVICEINFO', request = 'DEVICEINFO\n\r' (byte)
        '''
        request = ' '.join(map(str,args))
        request = (request + '\n\r').encode()
        return request

    
    def send_request_get_response(self,*args):
        '''
        Sends request to device over serial port and returns response.
        '''
        try:
            request = self.request_gen(*args)
            response = self.device.write_read(cmd_str=request,use_readline=True,check_write_freq=False,delay_write=True)
        except ReadError:
            self.close()
        response = response.strip()
        return response
    
    def device_info(self):
        '''
        Get device_info. Like "Mightex LED Driver:3.1.6 Device Module No.:SLC-AV04-U Device Serial No.:04-170824-012"
        '''
        request = 'DEVICEINFO'
        response = self.send_request_get_response(request)
        return response
    
    def what_mode(self):
        '''
        Get working mode of the LED
        '''
        mode_list = ['DISABLE','NORMAL','STROBE','TRIGGER']
        response = self.send_request_get_response('?MODE',self.channel)
        response = (response.strip().decode())[-1]
        mode = mode_list[int(response)]
        return mode

    def set_mode(self, mode):
        '''
        Changing working mode of the LED. For the MightexLED we have, there are four mode: ['DISABLE','NORMAL','STROBE','TRIGGER']
        '''
        mode_list = ['DISABLE','NORMAL','STROBE','TRIGGER']
        try:
            mode_code = mode_list.index(mode)
            response = self.send_request_get_response('MODE',self.channel,mode_code)  
        except:
            print('Mode is not correct, need to chose from DISABLE,NORMAL,STROBE,TRIGGER]')
            self.close()
                
    def normal_current_info(self):
        '''
        Get information on current (mA), result will show max current and setting current
        '''
        response = self.send_request_get_response('?CURRENT',self.channel)
        response = str(response).split(' ')
        current_max = str(response[-2])+'mA'
        current = str(response[-1])
        current = current[:len(current)-1]+'mA'
        return print ('Max current='+current_max+' ; '+'current='+current)

    def set_normal_parameters(self, current_max, current):
        response = self.send_request_get_response('NORMAL',self.channel,current_max,current)
        pass

    def set_current(self, current):
        '''
        Set current value of the LED in mA in NORMAL mode
        '''
        response = self.send_request_get_response('CURRENT',self.channel,current)
        pass


    def close(self):
        '''
        Close the device serial port. If the port is not close, you will have to restart the kernal to run another LED sequence.
        '''
        self.device.close()
'''
*Team id: eYRC-LM#448
*Author List: Akhil Guttula, Sai Kiran, Sai Gopal, Mohan
*Filename: comm.py
*Theme: Launch a Module
*Functions:init_serial,send_data
*Global Variables:ser
'''
import serial
import cv2

#ser: global variable used for communication
ser=0;

'''
*Function Name: init_serial
*Input: NULL
*Output: initialises a serial communication through xbee setting the parameters like com port,baudrate,bytesize,parity,stopbits
*Logic:using pyserial package
*Example Call: init_serial
'''
#initialises the parameters for communication with xbee
def init_serial():
    global ser
    ser = serial.Serial('COM3')
    ser.baudrate = 9600
    ser.bytesize = 8
    ser.parity = 'N'
    ser.stopbits = 1

'''
*Function Name: send_data
*Input: array of characters to be sent
*Output: array of characters are sent via serial communication
*Logic:using pyserial package
*Example Call: send_data
'''
#function used to send data to xbee
def send_data(data_input):
    global ser
    ser.write(data_input)

#initialises the xbee
init_serial()

    

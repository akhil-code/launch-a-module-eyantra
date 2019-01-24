import serial
import cv2

ser=0;
#initialises the parameters for communication with xbee
def init_serial():
    global ser
    ser = serial.Serial('COM3')
    ser.baudrate = 9600
    ser.bytesize = 8
    ser.parity = 'N'
    ser.stopbits = 1

#function used to send data to xbee
def send_data(data_input):
    global ser
    ser.write(data_input)

#initialises the xbee
init_serial()

    

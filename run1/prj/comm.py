import serial
import cv2

ser=0;

def init_serial():
    global ser
    ser = serial.Serial('COM3')
    ser.baudrate = 9600
    ser.bytesize = 8
    ser.parity = 'N'
    ser.stopbits = 1

def send_data(data_input):
    global ser
    ser.write(data_input)


init_serial()
#send_data('good')

    

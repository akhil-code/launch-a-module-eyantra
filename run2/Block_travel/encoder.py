import serial
import sys
import math
import comm
import time

def move(dist):
    pass


def move(dist):

    time_delay = abs(dist *(3500/360))
    time_delay = int(time_delay)

    comm.send_data('<d');cv2.waitKey(100);
    
    s = str(dist)
    length = len(s)

    while(length>0):
        digit = dist/math.pow(10,length-1)
        dist = dist%math.pow(10,length-1)
        length = length - 1
        comm.send_data(str(digit));time.sleep(0.1)

    comm.send_data('>');cv2.waitKey(100);
    #cv2.waitKey(time_delay)

move(int(sys.argv[1]))

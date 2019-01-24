import comm
import time

#moves the bot forward
def move_forward(time_delay):
    comm.send_data('8')
    time.sleep(time_delay)
    comm.send_data('5')
    time.sleep(75)


#hard rotates the bot by the angle specified
def rotate(ang):
    global ser_delay,add_delay

    time_delay = abs(ang * (3700/360.0))
    time_delay = int(time_delay)

    if(ang<0):
        comm.send_data('<a');time.sleep(ser_delay);
    else:
        comm.send_data('<k');time.sleep(ser_delay);

    ang = abs(ang)

    if(ang > 99):
        d = ang/100
        n = ang - 100*d
        comm.send_data(str(d));time.sleep(ser_delay);
        comm.send_data(str(n));time.sleep(ser_delay);
    else:
        comm.send_data(str(ang));time.sleep(ser_delay);

    comm.send_data('>');time.sleep(ser_delay);

    if(abs(ang) < 10 ):
        time_delay = time_delay + 100

    if(time_delay != 0):
        time.sleep(time_delay+add_delay)
    else:
        time.sleep(100)

ser_delay = 50
add_delay = 70

for x in range(10):
    move_forward(100)
    rotate(30)
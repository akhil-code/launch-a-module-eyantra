#ideal camera delay 15fps * 4 sec delay
#even: 11fps * 4sec delay also works
#serial delay with 40 ms is good
#serial delay with 30 ms also works
import cv2
import numpy as np
import math
import sys

import comm
import angle_mod
import algo_mod

def getxy(pos,img):
    global row_margin
    rows,cols,_ = img.shape

    #finds the row no and column no w.r.t position no
    c = pos%9
    if(c == 0):
        c = 9
        r = pos/9
    else:    
        r = (pos/9) +1
    #finds the starting and ending pixels
    cols_start = (c-1)*(cols/9)
    cols_end = c *(cols/9)
    rows_start = (r-1)*(rows/6)
    rows_end = r*(rows/6)

    x = (cols_start+cols_end)/2
    y = (rows_start+rows_end)/2
    return (x,y)


def soft_rotate(ang):
    global ser_delay
    
    time_delay = abs(ang * (5040/360.0))
    time_delay = int(time_delay)


    if(ang<0):
        comm.send_data('<q');cv2.waitKey(ser_delay);
    else:
        comm.send_data('<w');cv2.waitKey(ser_delay);

    ang = abs(ang)

    if(ang > 99):
        d = ang/100
        n = ang - 100*d
        comm.send_data(str(d));cv2.waitKey(ser_delay);
        comm.send_data(str(n));cv2.waitKey(ser_delay);
    else:
        comm.send_data(str(ang));cv2.waitKey(ser_delay);

    comm.send_data('>');cv2.waitKey(ser_delay);
    if(time_delay != 0):
        cv2.waitKey(time_delay)

def find_bot(capf,forward_values,backward_values):
    global row_margin
    rows,cols,_ = capf.shape
    bot_f = bot_c = (0,0)

    blur_img = cv2.bilateralFilter(capf,7,50,50)
    blur_img = cv2.medianBlur(blur_img,5)
    capy = cv2.cvtColor(blur_img,cv2.COLOR_BGR2HSV)
    img_temp = np.ones(capy.shape,np.uint8)#empty image to display the result

    for dir in range(2):
        if(dir == 0):
            low_values = forward_values[0]
            high_values = forward_values[1]
        else:
            low_values = backward_values[0]
            high_values = backward_values[1]

           
        #color filtering
        mask = cv2.inRange(capy,low_values,high_values)
        #opening
        mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
        mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
        #closing
        mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
        mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
        #cv2.imshow('mask',mask)
        
        #finding contours of the thresholded image
        ctrs,hierachy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(img_temp, ctrs,-1, (255,255,255), 2)
        
        
        for no in range(len(ctrs)):
            if cv2.contourArea(ctrs[no])>500:
                #centroid
                M = cv2.moments(ctrs[no])
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                
                if (dir == 0):
                    bot_f = (cx,cy)
                    #print 'for:'+str(bot_f)
                else:
                    #bot_c = ((cx+bot_f[0])/2,(bot_f[1]+cy)/2)
                    bot_c = (cx,cy)
                    #print 'cent:'+str(bot_c)
        
        cv2.putText(img_temp,str(dir),(cx,cy),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1,(255,255,255),2)
    return bot_f,bot_c,img_temp

def rotate(ang):
    global ser_delay

    time_delay = abs(ang * (3000/360.0))
    time_delay = int(time_delay)

    if(ang<0):
        comm.send_data('<a');cv2.waitKey(ser_delay);
    else:
        comm.send_data('<k');cv2.waitKey(ser_delay);

    ang = abs(ang)

    if(ang > 99):
        d = ang/100
        n = ang - 100*d
        comm.send_data(str(d));cv2.waitKey(ser_delay);
        comm.send_data(str(n));cv2.waitKey(ser_delay);
    else:
        comm.send_data(str(ang));cv2.waitKey(ser_delay);

    comm.send_data('>');cv2.waitKey(ser_delay);
    if(time_delay != 0):
        cv2.waitKey(time_delay)

def move(dis_px):
    global ser_delay

    if(dis_px > 100000):
        dis_cm = dis_px*(30/5041.0)
        dis_cm = int(dis_cm)
    elif(dis_px <= 100000 and dis_px > 15000):
        dis_cm = dis_px *(45/5041.0)
        dis_cm = int(dis_cm)
    elif(dis_px <= 15000):
        dis_cm = dis_px *(45/5041.0)
        dis_cm = int(dis_cm)
    
    t_delay = (5540/1000.0)*dis_cm
    t_delay = int(t_delay)

    val_str = str(dis_cm)
    length = len(val_str)

    comm.send_data('<d');cv2.waitKey(ser_delay)

    while(length > 1):
        d = int(dis_cm/math.pow(10,length-2))
        dis_cm = dis_cm % math.pow(10,length-2)
        comm.send_data(str(d));cv2.waitKey(ser_delay)
        length = length - 2
    if(dis_cm != 0):
        comm.send_data(str(int(dis_cm)));cv2.waitKey(ser_delay)
    comm.send_data('>');cv2.waitKey(ser_delay)
    if(t_delay != 0):
        cv2.waitKey(t_delay)

def move_forward(time_delay):
    comm.send_data('8')
    cv2.waitKey(time_delay)
    comm.send_data('5')

def pwm_reset():
    global ser_delay
    comm.send_data('<v');cv2.waitKey(ser_delay)
    comm.send_data('25');cv2.waitKey(ser_delay)
    comm.send_data('5>');cv2.waitKey(ser_delay)

def dir_rotate(curr_pos,bf,bc,angle):
    neigh = algo_mod.get_neighbours(curr_pos)
    missing = None
    left = right = -1
    
    angle_hor = angle_mod.angleof(bf,bc)
    print 'angle_hor: '+str(angle_hor)+' curr_pos: '+str(curr_pos)
    if( abs(angle_hor) <= 45):
        #horizontal right
        left = curr_pos -9
        right = curr_pos + 9
    elif( angle_hor >= 45 and angle_hor <= 135):
        #vertically down
        left = curr_pos + 1
        right = curr_pos -1
    elif((angle_hor >= 135 and angle_hor <= 180) or(angle_hor >= -180 and angle_hor <= -135)):
        #horizontally left
        left = curr_pos+9
        right = curr_pos -9
    elif(angle_hor >= -135 and angle_hor <= -45):
        #vertically up
        left = curr_pos -1
        right = curr_pos +1

    print 'left'+str(left)+'right'+str(right)
    if( angle > 0):
        try:
            neigh.index(right)
            print 'ACTUAL ROTATE: ' +str(angle)
            rotate(angle)
            return
        except ValueError:
            angle = angle - 360
            print 'ACTUAL ROTATE: ' +str(angle)
            rotate(angle)
            return
    
    elif(angle < 0):
        try:
            neigh.index(left)
            rotate(angle)
            print 'ACTUAL ROTATE: ' +str(angle)
            return
        except ValueError:
            angle = angle + 360
            print 'ACTUAL ROTATE: ' +str(angle)
            rotate(angle)
            return    

def find_critical_pts(route):
    target_pts = []
    diff = 99999
    temp_diff = 99999
    target_pts.append(route[0])
    for i in range(1,len(route)):
        temp_diff = route[i] - route[i-1]
        if(diff != 99999):
            if(diff != temp_diff):
                target_pts.append(route[i-1])
                diff = temp_diff
        diff = temp_diff
    target_pts.append(route[-1])
    return target_pts

def findBlockColor(point,img):
    global row_margin
    x = point[0]
    y = point[1]
    row,col,_ = img.shape
    img = img[row_margin:rows-row_margin,0:col]
    row,col,_ = img.shape

    c = math.ceil(x/(col/9.0))
    r = math.ceil(y/(row/6.0))
    return (r,c)

def getPositionFromCoord(point):
    r = point[0]
    c = point[1]
    return int(c+(r-1)*9)


############################################################################################################


row_margin = 25
col_margin = 0
cam_delay = 4
ser_delay = 40

#pwm_reset()


algo_mod.set_objects_positions([1,9,10,19,28,37,46,6,9,13,20,24,31,41,44,48])

#threshold values for far region to the destination
thresh_ang = 10
thresh_dis_far = 3000
thresh_dis_near = 600

backward_values = ((122,43,0),(165,135,255))
forward_values = ((120,90,0),(180,135,255))


cap = cv2.VideoCapture(1)
comm.send_data('o')


#for obj in matches:
for zeta in range(2):  
    
    if(zeta == 0):
        route_planned = algo_mod.find_route(int(sys.argv[1]),int(sys.argv[2]),1,1)
        route_planned = find_critical_pts(route_planned)
        print route_planned
    else:
        route_planned = algo_mod.find_route(int(sys.argv[2]),int(sys.argv[3]),1,1)
        route_planned = find_critical_pts(route_planned)
        print route_planned
        
    z = 11
    capz = 0
    while(z>0):
        _,capz = cap.read()
        cv2.waitKey(cam_delay)
        z = z-1
        
    rows,cols,_ = capz.shape
    capz = capz[row_margin:rows-row_margin,col_margin:]
        
    for i in range(1,55):
        cv2.circle(capz,getxy(i,capz),1,(0,0,255),cv2.CV_AA)
    cv2.imshow('centroids',capz)

    for index in range(len(route_planned)):
        
        bf,bc,img_temp = find_bot(capz,forward_values,backward_values)
        dest = getxy(route_planned[index],capz)

        if(route_planned[index] == int(sys.argv[2]) or route_planned[index] == int(sys.argv[3])):
            thresh_dis_near = 1600
            thresh_dis_far = 4000
        
        while(True):
            capz = 0
            z = 11
            while(z>0):
                _,capz = cap.read()
                cv2.waitKey(cam_delay)
                z = z-1
            #cropping the image
            rows,cols,_ = capz.shape
            capz = capz[row_margin:rows-row_margin,col_margin:]
            cv2.imshow('botc',capz)

            bf,bc,img_temp = find_bot(capz,forward_values,backward_values)
            cv2.line(img_temp,bc,dest,(255,255,255),1)
            cv2.imshow('bot',img_temp)

            angle = angle_mod.angle_between(bf,dest,bc)
            
            distance = (dest[0]-bc[0])*(dest[0]-bc[0]) + (dest[1]-bc[1])*(dest[1]-bc[1])
            print str(angle) +" , "+ str(distance)

            if(abs(angle) > thresh_ang and distance > thresh_dis_near):
                print '\t\t\t\ ROTATE: '+str(angle)
                mid_bot = [0,0]
                mid_bot[0] = (bc[0]+bf[0])/2
                mid_bot[1] = (bc[1]+bf[1])/2
                curr_pos = getPositionFromCoord(findBlockColor(mid_bot,capz))
                if(abs(angle) > 105):
                    dir_rotate(curr_pos,bf,bc,angle)
                    #rotate(angle)
                else:
                    soft_rotate(angle)

            elif(distance < thresh_dis_near):
                print 'REACHED INNER REGION'
                if(abs(angle) > thresh_ang):
                    soft_rotate(angle)
                    
                if(zeta == 0 and route_planned[index] == int(sys.argv[2])):
                    cv2.waitKey(10);comm.send_data('c')
                if(zeta == 1 and route_planned[index] == int(sys.argv[3])):
                    cv2.waitKey(10);comm.send_data('o')
                break

            
            
            elif(distance > thresh_dis_far):
                print '\t\t\t\t FORWARD FAR'
                move(distance)


            elif( distance > thresh_dis_near and distance < thresh_dis_far):
                print '\t\t\t\t FORWARD NEAR'
                k = 10
                t = distance/k
                move_forward(t)






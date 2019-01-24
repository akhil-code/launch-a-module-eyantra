'''
*Team id: eYRC-LM#448
*Author List: Akhil Guttula, Sai Kiran, Sai Gopal, Mohan
*Filename: task.py
*Theme: Launch a Module
*Functions: move,soft_rotate,rotate,find_bot,move_forward,move_backward,pwm_reset,getROI,getPositionFromCoord,findBlockColor,
            getCoord,getxy,find_critical_pts,find_critical_pts_mod,dir_rotate
*Global Variables:row_margin_top,row_margin_bottom,col_margin_left,col_margin_right,src_img,shapes,
                    colors,centroids,contour_areas,matches,values,cap,cam_delay,no_of_frames,ser_delay,add_delay,soft_flag,cmd_count

'''
# NOTE: change the COM PORT in the comm.py file(in the 'init_serial' function) when executing the code
# NOTE: certain parameters are adjusted in accordance with the position and height of camera and are commented such as '#old:1000', 
#       please change these parameters when calibrating

import cv2
import numpy as np
import cv2.cv as cv
import math
import sys
import time

# NOTE: change the COM PORT in the comm.py file(in the 'init_serial' function) when executing the code
import comm         #communication module
import algo_mod     #shortest path algorithm module
import angle_mod    #finds the angle (module)

'''
*Function Name: nothing
*Input: x
*Output: NULL
*Logic:empty function used for trackbar
*Example Call: nothing(x)
'''
def nothing(x):
    pass

'''
*Function Name: getxy
*Input: position,image captured
*Output: (x,y) coordinates of the centroid
*Logic: centroid is considered as the mean of starting and ending values of rows and columns of particular block
*Example Call: getxy(20,capz)
'''
def getxy(pos,img):
    rows,cols,_ = img.shape
    #finds the row no and column no w.r.t position no
    c = pos%9
    if(c == 0):
        c = 9
        r = pos/9
    else:    
        r = (pos/9) +1
    
    #finds the starting and ending pixels
    w_s = (19.8/186.4)*cols
    w_l = (20.971/186.4)*cols
    h_s = (19.8/124.7) *rows
    h_l = (21.275/124.7)*rows
    
    
    if( c == 1 or c == 9 ):
        if(c == 1):
            cols_start = 0
            cols_end = w_s
        elif(c ==9):
            cols_start = cols - w_s
            cols_end = cols
    else:
        cols_start = (c-2)*w_l + w_s
        cols_end = (c-1)*w_l + w_s

    if( r == 1 or r == 9):
        if(r == 1):
            rows_start = 0
            rows_end = h_s
        else:
            rows_start = rows - h_s
            rows_end = rows
    else:
        rows_start = (r-2)*h_l + h_s
        rows_end = (r-1)*h_l + h_s

    #centre
    x = (cols_start+cols_end)/2
    y = (rows_start+rows_end)/2
    
    if(pos >= 1 and pos <= 9):
        y = y - 12
    if(pos % 9 == 2):
        x = x - 16

    x = int(x)
    y = int(y)

    return (x,y)

'''
*Function Name: move
*Input: distance in pixels
*Output: serial commmunication command through xbee to move the robot
*        forward
*Logic:converts the pixel distance to distance in mm
*Example Call: move(8000)
'''
def move(dis_px):
    #dis_px: distance in pixels(range: >0)
    global ser_delay,add_delay

    #moves the bot to a distance depending on how far it is from the robot 
    if(dis_px > 150000):
        dis_cm = dis_px*(12/5041.0)#25
        dis_cm = int(dis_cm)
    elif(dis_px < 150000 and dis_px >= 100000 ):
        dis_cm = dis_px*(12/5041.0)#25
        dis_cm = int(dis_cm)
    
    elif(dis_px <= 100000 and dis_px > 25000):
        #old: 18,21,26(1),30(2),32(3),35(4)
        dis_cm = dis_px *(38/5041.0)#45
        dis_cm = int(dis_cm)

    elif(dis_px <= 25000 and dis_px > 15000):
        #old: 38,42,44(1),45(2),47(4)
        dis_cm = dis_px *(49/5041.0)#45
        dis_cm = int(dis_cm)
    elif(dis_px <= 15000 and dis_px>=6000):
        #old:39,42
        dis_cm = dis_px *(44/5041.0)#45
        dis_cm = int(dis_cm)
    elif(dis_px <= 6000):
        dis_cm = dis_px *(28/5041.0)#45
        dis_cm = int(dis_cm)
    
    #old: 5540
    #t_delay: time delay allowing the robot to move after sending a command
    #calculates how much time delay have to be provided depending on how far the robot is from the destination
    t_delay = (5000/1000.0)*dis_cm
    t_delay = int(t_delay)

    #val_str: converts the distance value into string to know how many digits are present in the integer
    val_str = str(dis_cm)
    #length: stores no of digits in the distace
    length = len(val_str)

    #sends serial command to move to distance in the format <ddistance> followed by a delay
    comm.send_data('<d');cv2.waitKey(ser_delay)

    while(length > 1):
        d = int(dis_cm/math.pow(10,length-2))
        dis_cm = dis_cm % math.pow(10,length-2)
        comm.send_data(str(d));cv2.waitKey(ser_delay)
        length = length - 2
    if(dis_cm != 0):
        comm.send_data(str(int(dis_cm)));cv2.waitKey(ser_delay)
    comm.send_data('>');cv2.waitKey(ser_delay)
    #waits for the operation to compelete
    if(t_delay != 0):
        cv2.waitKey(t_delay+add_delay)
    else:
        cv2.waitKey(50)

'''
*Function Name: soft_rotate
*Input: angle in degrees
*Output: serial commmunication command through xbee to soft rotate the robot
*Logic:sends the angle to be rotated as <qdegrees> for anti-clockwise rotation
        and <wdegrees> for clock-wise rotation
*Example Call: soft_rotate(45)
'''
#soft rotates the robot by the angle specified
#input:angle
def soft_rotate(ang):
    global ser_delay,add_delay
    #old:6230
    #time_delay: time delay allowing the robot to move after sending a command
    #calculates how much time delay have to be provided depending on how much it has to rotate
    time_delay = abs(ang * (4400/360.0))
    time_delay = int(time_delay)

    #sending the serial commands in the format <adegrees> for anti-clockwise and <kdegrees> for clockwise direction
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
    
    #waits for the operation to compelete
    if(abs(ang) < 10 ):
        time_delay = time_delay + 50
    if(time_delay != 0):
        cv2.waitKey(time_delay+add_delay)
    else:
        #old:100
        cv2.waitKey(50)


'''
*Function Name: rotate
*Input: angle in degrees
*Output: serial commmunication command through xbee to hard/sharp rotate the robot
*Logic:sends the angle to be rotated as <qdegrees> for anti-clockwise rotation
        and <wdegrees> for clock-wise rotation
*Example Call: rotate(45)
'''
#hard rotates the bot by the angle specified
def rotate(ang):
    global ser_delay,add_delay
    #old 3700
    time_delay = abs(ang * (2500/360.0))
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

    if(abs(ang) < 10 ):
        time_delay = time_delay + 50

    if(time_delay != 0):
        cv2.waitKey(time_delay+add_delay)
    else:
        cv2.waitKey(100)


'''
*Function Name: find_bot
*Input: captured image,threshold values for front color of robot,threshold values for back color of robot
*Output: returns the coordinates for forward and backward and image containing contours of the both
*Logic: uses inRange function to threshold the image(HSV-color space)
*Example Call:find_bot(capz,(10,13,45),(180,255,255))
'''
#finds the position and the orientation of the bot in the arena
def find_bot(capf,forward_values,backward_values):
    rows,cols,_ = capf.shape
    bot_f = bot_c = (0,0)
    cx = cy = 0

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
        mask = cv2.dilate(mask,np.ones((7,7),np.uint8),iterations = 1)
        mask = cv2.erode(mask,np.ones((7,7),np.uint8),iterations = 1)
        #cv2.imshow('mask',mask)
        
        #finding contours of the thresholded image
        ctrs,hierachy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(img_temp, ctrs,-1, (255,255,255), 2)
        
        for no in range(len(ctrs)):
            if cv2.contourArea(ctrs[no])>200:
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

'''
*Function Name: move_forward
*Input: time for which the robot moves in the forward direction
*Output: robot moves in the forward direction (commands through xbee)
*Logic: sends command to move forward, waits for the time specified and then halts the robot
*Example Call:move_forward(1000)
'''
#moves the bot forward
def move_forward(time_delay):
    comm.send_data('8')
    cv2.waitKey(time_delay)
    comm.send_data('5')
    cv2.waitKey(75)

'''
*Function Name: move_backward
*Input: time for which the robot moves in the backward direction
*Output: robot moves in the backward direction (commands through xbee)
*Logic: sends command to move backward, waits for the time specified and then halts the robot
*Example Call:move_backward(1000)
'''
#moves the bot backward
def move_backward(time_delay):
    comm.send_data('2')
    cv2.waitKey(time_delay)
    comm.send_data('5')
    cv2.waitKey(75)

'''
*Function Name: pwm_reset
*Input: Null
*Output: Serial command to xbee(<v255>) to set the pwm of the firebird to 255
*Logic: send a serial command
*Example Call:pwm_reset()
'''
#resets the pwm of the bot to 255
def pwm_reset():
    global ser_delay
    comm.send_data('<v');cv2.waitKey(ser_delay)
    comm.send_data('25');cv2.waitKey(ser_delay)
    comm.send_data('5>');cv2.waitKey(ser_delay)

'''
*Function Name: getROI
*Input: image of arena, position to be cropped
*Output: ROI of the image for specific position
*Logic: crops the image by dividing the image into 9 columns and 6 rows of same dimensions
*Example Call:getROI(capz,12)
'''
#returns the ROI of the arena in accordance with the position specified
def getROI(img,pos):
    rows,cols = img.shape
    #finds the row no and column no w.r.t position no
    c = pos%9
    if(c == 0):
        c = 9
        r = pos/9
    else:    
        r = (pos/9) +1
    
    #finds the starting and ending pixels
    w_s = (19.8/186.4)*cols
    w_l = (20.971/186.4)*cols
    h_s = (19.8/124.7) *rows
    h_l = (21.275/124.7)*rows
    
    if( c == 1 or c == 9 ):
        if(c == 1):
            cols_start = 0
            cols_end = w_s
        elif(c ==9):
            cols_start = cols - w_s
            cols_end = cols
    else:
        cols_start = (c-2)*w_l + w_s
        cols_end = (c-1)*w_l + w_s

    if( r == 1 or r == 9):
        if(r == 1):
            rows_start = 0
            rows_end = h_s
        else:
            rows_start = rows - h_s
            rows_end = rows
    else:
        rows_start = (r-2)*h_l + h_s
        rows_end = (r-1)*h_l + h_s

    #return roi of calculated pixels
    temp_img =  img[rows_start:rows_end,cols_start:cols_end]
    return temp_img

'''
*Function Name: getPositionFromCoord
*Input: (row number,column number)
*Output: return the position on the arena ranging from 1 to 54
*Logic: the position in calculated using position = column no + no of columns * (row no - 1)
*Example Call:getPositionFromCoord((1,6))
'''
def getPositionFromCoord(point):
    r = point[0]
    c = point[1]
    return int(c+(r-1)*9)

'''
*Function Name: findBlockColor
*Input: coordinates of the point,image captured
*Output: (row no,column no)
*Logic: divides the image provided into equal segments of rows and columns and locates the block into which the point provided falls
*Example Call:findBlockColor((100,250),capz)
'''
def findBlockColor(point,img):
    x = point[0]
    y = point[1]
    rows,cols,_ = img.shape

    w_s = (19.8/186.4)*cols
    w_l = (20.971/186.4)*cols
    h_s = (19.8/124.7) *rows
    h_l = (21.275/124.7)*rows

    if(x >= 0 and x <= w_s):
        c = 1
    elif( x <= cols and x >= (cols - w_s)):
        c = 9
    else:
        x = x-w_s
        c = math.ceil(x/((cols-2*w_s)/7.0)) + 1

    if( y >= 0 and y <= h_s):
        r = 1
    elif( y <= rows and y >= (rows - h_s)):
        r = 6
    else:
        y = y - h_s
        r = math.ceil(y/((rows - 2*h_s)/4.0)) + 1

    return (r,c)

'''
*Function Name: getCoord
*Input: block poisition no i.e 1 to 55
*Output: (row no,column no)
*Logic: column no = position % 9
*       row no = (position/9) + 1
*Example Call: getCoord(21)
'''
def getCoord(pos):
    c = pos%9
    if(c == 0):
        c = 9
        r = pos/9
        return (r,c)
    r = (pos/9) +1
    return (r,c)





'''
*Function Name: find_critical_pts
*Input: route from source to destination
*Output: return a list containing all those points which are the sharp points of the route 
*           i.e points till which robot can move in straight path with no change in direction
*Logic: removes all the unnecessary points in the path which fall in the straight path between the critical points
*Example Call: find_critical_pts([9,18,27,36,45,54,53,52,51,50,49,48,47,46])
'''
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

'''
*Function Name: find_critical_pts_mod
*Input: route from source to destination
*Output: return a list containing all those points which are the sharp points of the route leaving an intermediate point in between
*           i.e points till which robot can move in straight path with no change in direction and skipping only one block in between
*Logic: removes all the unnecessary points in the path which fall in the straight path between the critical points
*Example Call: find_critical_pts_mod([9,18,27,36,45,54,53,52,51,50,49,48,47,46])
'''
def find_critical_pts_mod(route):
    count = 0
    target_pts = []
    diff = 99999
    temp_diff = 99999
    target_pts.append(route[0])
    for i in range(1,len(route)):
        temp_diff = route[i] - route[i-1]
        if(diff != 99999):
            if(diff != temp_diff or count == 3):
                target_pts.append(route[i-1])
                diff = temp_diff
                count = 0
            else:
                count = count+1
        diff = temp_diff
    target_pts.append(route[-1])
    return target_pts

'''
*Function Name: dir_rotate
*Input: current position of the robot,coordinates of bot forward,backward,angle to which the robot has to be rotated
*Output: rotates the bot in the direction calculated based on the logic
*Logic: checks whether there is an object or obstacle to its left and right direction and then rotates the bot in the direction opposite to the direction in which there is an obstacle
*Example Call: dir_rotate(20,(100,140),(120,160),170)
'''
#checks whether there is a robot to the left or right of the robot
# and rotates in the direction opposite to the side of obstacle
def dir_rotate(curr_pos,bf,bc,angle):
    print 'curr_pos'+str(curr_pos)
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
            if(right < 1 or right > 54 or right % 9 == 1):
                pass
            else:
                neigh.index(right)              #checks if the space to right is free
            print 'ACTUAL ROTATE: ' +str(angle)
            rotate(angle)
            return
        except ValueError:
            angle = angle - 360
            print 'ACTUAL ROTATE: ' +str(angle)
            rotate(angle)
            cv2.waitKey(500)
            return
    
    elif(angle < 0):
        try:
            if(left > 54 or left < 1 or left % 9 == 1):
                pass
            else:
                neigh.index(left)               #checks if he space to the left is free
            rotate(angle)
            print 'ACTUAL ROTATE: ' +str(angle)
            return
        except ValueError:
            angle = angle + 360
            print 'ACTUAL ROTATE: ' +str(angle)
            rotate(angle)
            cv2.waitKey(500)
            return  

#################################################################################################################
# GLOBAL VARIABLES
#################################################################################################################
#used to crop the unnecessary parts of the arena
row_margin_top = 0
add_margin = 15
row_margin_bottom = 48
col_margin_left = 2
col_margin_right = 15
#rows = cols = 0
src_img = 0




#used to store the information regarding the properties of objects present in the arena

#shapes: stores the objects present in the location(index)-> 0:obstacle 1:circle 2:square 3:triangle
shapes = []
#colors: stores the color values->0:red 1:green 2:blue
colors=[]
#stores whether the working area objects are matched or not
matches_work_area = []

centroids = []
contour_areas = []
matches = []


#contains the color values(hsv-color space) of red,green,blue colors
values=[]
#values = [(138,69,70),(180,255,237),(25,124,20),(102,255,126),(95,124,45),(136,255,174)]
#values = [(57,152,180),(180,204,251),(57,137,56),(180,255,105),(121,167,56),(180,255,255)]
#values = [(167,144,145),(180,201,192),(9,93,49),(97,255,160),(90,105,92),(162,255,180)] #morning1
#values = [(170,100,98),(180,255,255),(20,21,0),(103,255,107),(93,155,41),(118,255,255)] #night1
#values = [(170,44,88),(180,255,255),(18,38,5),(105,255,140),(95,93,29),(117,255,255)]#night2
#values = [(168,0,43),(180,255,255),(60,85,13),(102,255,140),(90,25,65),(157,255,255)]#night3
#values = [(0,175,129),(180,255,255),(68,33,0),(108,253,123),(50,62,74),(129,244,255)]#night4
#values = [(0,175,128),(180,255,255),(70,28,23),(100,250,146),(93,87,52),(113,239,255)]#night4
#values = [(114,129,54),(180,255,255),(12,95,0),(103,255,136),(84,149,80),(111,250,255)]#night5
#values = [(115,131,67),(180,255,255),(65,75,21),(105,255,138),(97,75,21),(113,255,223)]#night6
#values = [(156,33,75),(180,255,255),(18,62,0),(105,255,138),(93,172,80),(138,255,255)]#evng1
#values = [(111,70,142),(180,255,255),(73,106,34),(100,255,126),(54,101,108),(116,255,255)]#evng2
#values = [(115,137,133),(180,255,255),(39,99,45),(104,232,133),(89,79,97),(121,207,170)]#evng2
#values = [(132,83,136),(180,255,255),(46,70,28),(111,255,131),(46,70,60),(111,203,255)]#night7
#values = [(112,74,146),(180,255,255),(65,138,31),(107,255,124),(65,138,82),(107,215,255)]#night7
#values = [(138,59,46),(180,255,255),(78,48,52),(106,255,151),(68,85,94),(118,255,198)]#night8
#values = [(113,63,147),(180,255,255),(66,63,25),(99,234,121),(75,149,84),(121,234,164)]#evng3
#values = [(106,126,141),(180,255,255),(61,118,27),(104,255,124),(50,60,109),(125,220,191)]#night 8
#values = [(112,141,112),(180,255,255),(72,117,36),(106,255,126),(95,59,96),(142,214,255)]#night 8
#values = [(163,130,93),(180,255,255),(59,54,11),(99,255,255),(59,54,66),(114,233,255)]#night 9
values = [(120,109,76),(180,255,255),(30,93,29),(113,255,129),(30,66,80),(113,211,255)]#night 9





##################################################################################################################
# MAIN CODE STARTS HERE
##################################################################################################################   

#initialisation
#cap: used to capture images for the entire program
cap = cv2.VideoCapture(1)

#resetting the arrays to "-1"
#stores from 0 to 54 but we use 1 to 54 w.r.t position
for x in range(55):
    shapes.append(-1)
    colors.append(-1)
    centroids.append(-1)
    contour_areas.append(-1)
    matches_work_area.append(-1)


for x in range(7):
    matches.append(-1)  

#captures the image of the arena for further processing
z = 50
while(z>0):
    #_,src_img_color = cap.read()
    #_,img_sv = cap.read()
    src_img_color = cv2.imread('img.jpg')
    
    #cv2.imshow('input',src_img_color)
    cv2.waitKey(10)
    z = z - 1

rows,cols,_ = src_img_color.shape

#changing color space from RBG to Gray scale image
img = cv2.cvtColor(src_img_color,cv2.COLOR_BGR2GRAY)

#otsu binarization: to detect the shapes
_,thresh_otsu = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#binary image invertion
thresh_inv = cv2.bitwise_not(thresh_otsu)
cv2.imshow('thresh',thresh_inv)


#cropping the unnecessary portion of the arena 
thresh_inv = thresh_inv[row_margin_top:rows-row_margin_bottom,col_margin_left:cols-col_margin_right]
cv2.imshow('input',src_img_color)
src_img_color = src_img_color[row_margin_top:rows-row_margin_bottom,col_margin_left:cols-col_margin_right]
#cv2.imshow('input',src_img_color)
#cv2.imshow('thresh_arena',thresh_inv)



#finding the shapes of the objects present in the arena
#using ratio of contour areas concept
for pos in range(1,55):
    # Skipping the position of the robot
    if(pos == 23):
        continue
    #taking ROI(Region of Interest)
    roi_img = getROI(thresh_inv,pos)
    if(pos >= 1 and pos <=9):
        roi_img = roi_img[add_margin:,:]
    cv2.imshow('otsu_roi',roi_img)
    #finding contours to find out the contour area for each ROI
    contours,hierachy = cv2.findContours(roi_img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #empty blank image
    img_temp = np.zeros(roi_img.shape, np.uint8)

    for no in range(len(contours)):
        #print cv2.contourArea(contours[no])
        if cv2.contourArea(contours[no])<60:
            continue


        try:
            #finding centroid
            M = cv2.moments(contours[no])
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])

            r,c = getCoord(pos)

            cx = cx + (c-1)*(cols - col_margin_left - col_margin_right)/9.0
            cy = cy + (r-1)*(rows - row_margin_top - row_margin_bottom)/6.0

            cx = int(cx)
            cy = int(cy)

            if(pos >= 1 and pos <=9):
                cy = cy+add_margin

            #finding minimum area rectangle
            rect = cv2.minAreaRect(contours[no])
            box = cv2.cv.BoxPoints(rect)
            box = np.int0(box)

            #finding the ratio of areas
            area_ratio = cv2.contourArea(contours[no])/cv2.contourArea(box)
        except ZeroDivisionError:
            print 'error: zero division: '+str(pos)

        #Applying contour area ratio to identify the shapes
        if(cv2.contourArea(contours[no]) > contour_areas[pos]):
            #rectangle
            if(area_ratio >0.85):
                print str(pos)+':rectangle\t'+'area ratio:'+str(area_ratio)+'\tcontour area: '+str(cv2.contourArea(contours[no]))
                shapes[pos] = 2
                contour_areas[pos] = cv2.contourArea(contours[no])
                centroids[pos] = (cx,cy)
            #circle
            elif(area_ratio > 0.65 and area_ratio <= 0.85):
                print str(pos)+':circle\t'+'area ratio:'+str(area_ratio)+'\tcontour area: '+str(cv2.contourArea(contours[no]))
                shapes[pos] = 1
                contour_areas[pos] = cv2.contourArea(contours[no])
                centroids[pos] = (cx,cy)
            #triangle
            elif(area_ratio <= 0.65 and area_ratio > 0.30):
                print str(pos)+':triangle\t'+'area ratio:'+str(area_ratio)+'\tcontour area: '+str(cv2.contourArea(contours[no]))
                shapes[pos] = 3
                contour_areas[pos] = cv2.contourArea(contours[no])
                centroids[pos] = (cx,cy)

         
#cropping the source image
blur_img = cv2.bilateralFilter(src_img_color,5,50,50)
blur_img = cv2.medianBlur(blur_img,5)
img = cv2.cvtColor(blur_img,cv2.COLOR_BGR2HSV)

# COLOR detection(RGB)
#red:0, green:1, blue:2
for x in range(3):

    print values[2*x]
    print values[(2*x)+1]

    #color filtering
    mask = cv2.inRange(img,values[2*x],values[(2*x)+1])
    #opening
    mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
    mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
    #closing
    mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
    mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)


    #finding contours of the thresholded image
    contours,hierachy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    img_temp = np.ones((480,640),np.uint8)#empty image to display the result

    for no in range(len(contours)):
        #print cv2.contourArea(contours[no])
        #if cv2.contourArea(contours[no])<10:
        #    continue
        
        #centroid
        M = cv2.moments(contours[no])
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        position = getPositionFromCoord(findBlockColor((cx,cy),src_img_color))
        position = int(position)
        cv2.putText(img_temp,str(no),(cx,cy),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1,(255,255,255),2)



        #min area rectangle
        rect = cv2.minAreaRect(contours[no])
        box = cv2.cv.BoxPoints(rect)
        box = np.int0(box)

        #identifying obstacles based on the property that they have larger contour area
        if(x == 0 and cv2.contourArea(box) > 500 and shapes[position] == -1 and position != 23):
            shapes[position] = 2


        try:
            if( shapes[position] != -1):
                colors[position] = x
        except:
            print 'error at: '+str(position)

    cv2.imshow('contours'+str(x),img_temp)


#prints the details of the objects that have been detected
for x in range(55):
    if(shapes[x] != -1):
        print 'pos:'+str(x)+'  Shape:'+str(shapes[x])+'  Area:'+str(contour_areas[x])+'  Centroid:'+str(centroids[x])+'  Colors:  '+str(colors[x])

#matching the results
print '\nMATCHES'
for x in (1,10,19,28,37,46):#make the values -1
    for y in range(1,55):
        ctr = getxy(y,src_img_color)
        cv2.putText(src_img_color,str(y),(ctr[0],ctr[1]),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,0.5,(255,255,255),2)
        if( x != y and shapes[x] != -1 and colors[x]!=-1 and shapes[x] == shapes[y] and colors[x] == colors[y] and matches_work_area[y] < 0):
            if(y%9 != 1 and abs(contour_areas[y] - contour_areas[x]) < 60):
                #matches.append((y,x))
                #if the doorway object has one match in working area
                if(matches[(x/9)+1] == -1):
                    matches[(x/9) + 1] = y
                #if the doorway object has more than one match in the working area 
                else:

                    match_new = centroids[y]
                    match_old = centroids[matches[(x/9)+1]]
                    match_shape = centroids[x]

                    diff_new = (match_shape[0]-match_new[0])*(match_shape[0]-match_new[0]) + (match_shape[1]-match_new[1])*(match_shape[1]-match_new[1])
                    diff_old = (match_shape[0]-match_old[0])*(match_shape[0]-match_old[0]) + (match_shape[1]-match_old[1])*(match_shape[1]-match_old[1])
                    
                    print 'diff_new: '+str(diff_new)+'\tdiff_old: '+str(diff_old)
                    if(diff_new < diff_old):
                        matches[(x/9)+1] = y

                print str((y,x))
    matches_work_area[matches[(x/9)+1]] = 1




match_pairs = []
for x in range(1,7):
    if(matches[x] != -1):
        match_pairs.append([matches[x],9*(x-1)+1])

#altering the objects matched with the door area
for x in range(len(match_pairs)-1):
    for y in range(x+1,len(match_pairs)):
        if(shapes[match_pairs[x][1]] == shapes[match_pairs[y][1]] and colors[match_pairs[x][1]] == colors[match_pairs[y][1]]):
            p1_x = centroids[match_pairs[x][1]]
            p1_y = centroids[match_pairs[x][0]]
            p2_x = centroids[match_pairs[y][1]]
            p2_y = centroids[match_pairs[y][0]]
            
            d1 = (p1_x[0]-p1_y[0])*(p1_x[0]-p1_y[0]) + (p1_x[1]-p1_y[1])*(p1_x[1]-p1_y[1])
            d2 = (p2_x[0]-p2_y[0])*(p2_x[0]-p2_y[0]) + (p2_x[1]-p2_y[1])*(p2_x[1]-p2_y[1])

            sum_comb = d1 + d2
            
            d1 = (p1_x[0]-p2_y[0])*(p1_x[0]-p2_y[0]) + (p1_x[1]-p2_y[1])*(p1_x[1]-p2_y[1])
            d2 = (p2_x[0]-p1_y[0])*(p2_x[0]-p1_y[0]) + (p2_x[1]-p1_y[1])*(p2_x[1]-p1_y[1])


            sum_comb_swap = d1 + d2
            print 'sum_comb: '+str(sum_comb)
            print 'sum_comb_swap: '+str(sum_comb_swap)
            if(sum_comb_swap <= sum_comb):
                temp_match = match_pairs[y][0]
                print temp_match
                match_pairs[y][0] = match_pairs[x][0]
                match_pairs[x][0] = temp_match


#plotting the lines on the source image showing the matches found with the door arena shapes
for x in match_pairs:
    cv2.line(src_img_color,getxy(x[0],src_img_color),getxy(x[1],src_img_color),(255,255,255),3)


sorted_match_pairs = []

#picking objects from top to bottom
for pos in range(1,55):
    if(pos%9 != 1):
        for obj in match_pairs:
            if(obj[0] == pos):
                sorted_match_pairs.append(obj)


match_pairs = sorted_match_pairs

print 'match pairs '+str(match_pairs)

cv2.imshow('matches',src_img_color)


#Asking the user to continue further if the matches are correct
print 'DO YOU WANT TO CONTINUE'

#if(cv2.waitKey(0) & 0xFF == ord('q')):
#    cv2.imwrite('img.jpg',img_sv)
#    sys.exit()

cv2.destroyWindow('contours0')
cv2.destroyWindow('otsu_roi')
cv2.destroyWindow('thresh_inv')
cv2.destroyWindow('contours1')
cv2.destroyWindow('contours2')


####################################################################################################################
# BOT MOVEMENT
####################################################################################################################

#cam_delay: delay that is induced between successive captures from the image
cam_delay = 4           
#no_of_frames: no of frames that have to be captured in order to empty the buffer
no_of_frames = 11      
#ser_delay: delay between successive bytes when communicating with xbee
ser_delay = 20 #old:40,30,20              
#add_delay: additional delay to be induced if required
add_delay = 0
#soft_flag: when set rotates the robot only in soft rotate mode
soft_flag = 0
#cmd_count: counts the no of commands executed during the traversal
cmd_count = 0

#lifts the hand of the robot in order to avoid the obstacles(only at begining of the bot movement)
comm.send_data('i');cv2.waitKey(100)
comm.send_data('o');cv2.waitKey(100)
 



#obstacles: contains the positions of the objects and obstacles in the arena through which bot can't traverse
obstacles = []              
for x in range(1,55):
    if(shapes[x] != -1):
        obstacles.append(x)
print 'obstacles: '+str(obstacles)

#next_pos_trav: stores the position where the bot currently is present         
next_pos_trav = 23

#invokes the algo_mod to set the objects positions
algo_mod.set_objects_positions(obstacles) #sets the positions of objects in the shortest path algorithm

#adding the c-5 as empty space
algo_mod.set_free_loc(23)
algo_mod.set_free_loc(22)
algo_mod.set_free_loc(24)
algo_mod.set_free_loc(14)




#threshold values for far region to the destination
#threshold angle(tolerance in the angle made by the robot with the destination)
thresh_ang = 3
#threshold distances 
thresh_dis_far = 2000       #old: 3000
thresh_dis_near = 1000       #old: 600

#forward and backward colors of the bot(HSV-color space)
forward_values = ((137,70,191),(180,132,255))
backward_values = ((1,65,155),(168,142,231))


#directions for the traversal of the bot
#for each pair of the working area object and doorway shape
for obj in match_pairs:
    #zeta = 0 for traveral to the source(working area object) and zeta = 1 for traversal to the destination(door way)
    for zeta in range(2):  
        #finding route between the source and the destination
        if(zeta == 0):
            #finding the route between current position and source
            route_planned = algo_mod.find_route(next_pos_trav,obj[0],1,1)
            route_planned = find_critical_pts_mod(route_planned)
            print 'routing between ' + str(next_pos_trav)+' ,'+str(obj[0])
            print 'routed: '+str(route_planned)
        else:
            #finding the route between object to the corresponding doorway shape
            print 'routing between ' + str(obj[0])+' ,'+str(obj[1])
            route_planned = algo_mod.find_route(obj[0],obj[1],1,1)
            print 'raw_route '+str(route_planned)
            route_planned = find_critical_pts_mod(route_planned)
            print 'routed: '+str(route_planned)
        
        #captures the image from camera while looping for few seconds
        z = no_of_frames
        capz = 0
        while(z>0):
            _,capz = cap.read()
            cv2.waitKey(cam_delay)
            z = z-1
        
        #cropping the unnecessary portion of the image using the margin values
        rows,cols,_ = capz.shape
        capz = capz[row_margin_top:rows-row_margin_bottom,col_margin_left:cols - col_margin_right]
        
        #marks the centroids on the image captured
        for i in range(1,55):
            cv2.circle(capz,getxy(i,capz),1,(0,0,255),cv2.CV_AA)
            if(centroids[i] != -1):
                cv2.circle(capz,centroids[i],1,(255,0,0),cv2.CV_AA)
        cv2.imshow('centroids',capz)


        #traversing throught each point in the route
        for index in range(len(route_planned)):
            #sets the threshold distance(the threshold distance will be far when the destination is a object or doorway shape)
            if(route_planned[index] == obj[0] or route_planned[index] == obj[1]):
                thresh_dis_far = 6500       #3000
                thresh_dis_near = 3700
                soft_flag = 0
            #sets the threshold distance(the distance will be nearer when the destination is an empty location)
            else:
                thresh_dis_far = 1900       #3000
                thresh_dis_near = 1000
            
            #finds the coordinates of the destination point
            dest = getxy(route_planned[index],capz)
            
            if(route_planned[index] == 1):
                cx = dest[0]
                cy = dest[1]
                
                cy = cy+ 0.08*cy
                cy = cy - 10
                dest = (cx,cy)


            #replaces the coordinates of the block with the coordinates of the shape or object if the destination to be reached is an object or doorway shape
            if(route_planned[index] == obj[0]):
                print 'dest '+str(dest)+' ,centroids '+ str(centroids[obj[0]])
                dest = centroids[obj[0]]
                print 'after dest '+str(dest)+' ,centroids '+ str(centroids[obj[0]])
            elif(route_planned[index] == obj[1]):
                dest = centroids[obj[1]]

            #runs infintely untill the intermediate desination is reached
            while(True):
                #counts the number of commands executed
                cmd_count = cmd_count + 1
                #capturing image
                capz = 0
                z = no_of_frames
                while(z>0):
                    _,capz = cap.read()
                    cv2.waitKey(cam_delay)
                    z = z-1

                #cropping the image
                rows,cols,_ = capz.shape
                capz = capz[row_margin_top:rows-row_margin_bottom,col_margin_left:cols-col_margin_right]
                #cv2.imshow('botc',capz)

                #finds bot location else moves the bot backward
                try:
                    bf,bc,img_temp = find_bot(capz,forward_values,backward_values)

                    mid_bot = [0,0]
                    mid_bot[0] = int((bc[0]+bf[0])/2)
                    mid_bot[1] = int((bc[1]+bf[1])/2)
                    mid_bot = (mid_bot[0],mid_bot[1])
                    curr_pos = getPositionFromCoord(findBlockColor(mid_bot,capz))
                    print 'curr_pos'+ str(curr_pos)
                except:
                    move_backward(500)
                    cv2.waitKey(1000)
                    continue
                #marks a line between the bot and the intermediate destination
                cv2.line(img_temp,mid_bot,dest,(255,255,255),1)
                cv2.imshow('bot',img_temp)

                #finds angle and distance
                angle = angle_mod.angle_between(bf,dest,bc)
                distance = (dest[0]-mid_bot[0])*(dest[0]-mid_bot[0]) + (dest[1]-mid_bot[1])*(dest[1]-mid_bot[1])
                print 'bot: '+str(angle) +" , "+ str(distance)
                
                #if the distance is far away and angle is greater than the threshold
                if(abs(angle) > thresh_ang and distance > thresh_dis_near):
                    print '\t\t\t\t ROTATE: '+str(angle)
                    atBorder = False
                    if((curr_pos >= 1 and curr_pos <=9) or (curr_pos % 9 == 0) or (curr_pos >= 46 and curr_pos <=54)):
                        atBorder = True
                    if( abs(angle) <= 5):
                        if(angle > 0):
                            angle  = 8
                        elif(angle < 0):
                            angle = -8
                    if( abs(angle) > 100):
                        move_forward(150)
                        #old:300
                        cv2.waitKey(150)
                        rotate(angle)
                        soft_flag = 1
                    elif(soft_flag == 1 and (not atBorder)):
                        if(distance > 5500 and curr_pos %9 != 2):
                            soft_rotate(angle)
                        else:
                            move_forward(150)
                            #old: 300
                            cv2.waitKey(150)
                            rotate(angle)

                    else:
                        rotate(angle)
                        soft_flag = 1
                    
                #if the bot reached the destination adjust the angle and break the loop i.e to the next object
                elif(distance < thresh_dis_near):
                    print 'REACHED INNER REGION'
                    if(abs(angle) > thresh_ang):
                        if(soft_flag == 1):
                            soft_rotate(angle)
                        else:
                            rotate(angle)
                            soft_flag = 1

                    if(zeta == 0 and route_planned[index] == obj[0]):
                        cv2.waitKey(100);
                        #picking up the object
                        #old: 2100
                        comm.send_data('X');cv2.waitKey(2100)
                        #old:325
                        move_forward(400)
                        #old:1000
                        cv2.waitKey(300)#push forward
                        
                        soft_flag = 0
                        algo_mod.set_free_loc(obj[0])
                        algo_mod.set_free_loc(next_pos_trav)
                        break
                    elif(zeta == 1 and route_planned[index] == obj[1]):
                        cv2.waitKey(10);
                        #dropping down the object
                        comm.send_data('I');cv2.waitKey(2100)
                        #moves backward a bit after deposition of the object in doorway
                        move_backward(250)
                        print 'set free loc '+str(obj[0])
                        #sets the location of object free
                        
                        algo_mod.set_free_loc(obj[0])
                        algo_mod.set_free_loc(next_pos_trav)

                        #sets the next postion to traverse as neighbouring position to the current previous doorway shape
                        next_pos_trav = obj[1]+1
                        soft_flag = 0
                        break
                    break

            
                elif(distance > thresh_dis_near and distance < thresh_dis_far):
                    print '\t\t\t\t FORWARD MID'
                    move_forward(150)
                elif(distance > thresh_dis_far):
                    print '\t\t\t\t MOVING:'+str(distance)
                    move(distance)

cv2.waitKey(1000)
comm.send_data('O');cv2.waitKey(7000)
comm.send_data('C');cv2.waitKey(100)
print 'cmd_count: '+str(cmd_count)


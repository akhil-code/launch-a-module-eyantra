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

#cv2: opencv library
import cv2
import cv2.cv as cv
#numpy: numpy library
import numpy as np
#other libraries used
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
    
    #shifting the centroids to adjust the slant view of the arena
    x = x + 0.01*x
    y = y + 0.01*y

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
    #the multiplication factor determines how far the bot moves with respect to the actual distance
    if(dis_px > 150000):
        dis_cm = dis_px*(12/5041.0)
        dis_cm = int(dis_cm)
    elif(dis_px < 150000 and dis_px >= 100000):
        dis_cm = dis_px*(12/5041.0)#25
        dis_cm = int(dis_cm)
    
    elif(dis_px <= 100000 and dis_px > 25000):
        dis_cm = dis_px *(38/5041.0)#45
        dis_cm = int(dis_cm)

    elif(dis_px <= 25000 and dis_px > 15000):
        dis_cm = dis_px *(49/5041.0)#45
        dis_cm = int(dis_cm)
    elif(dis_px <= 15000 and dis_px>=6000):
        dis_cm = dis_px *(44/5041.0)#45
        dis_cm = int(dis_cm)
    elif(dis_px <= 6000):
        dis_cm = dis_px *(28/5041.0)#45
        dis_cm = int(dis_cm)
    
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
                else:
                    bot_c = (cx,cy)
        
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
    #(since the blocks are of small size at the border when compared to the rest, so the the blocks are cropped smaller at borders)
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
    
    #(since the blocks are of small size at the border when compared to the rest, so the the blocks are considered smaller at borders)
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
        by checking if the difference of the next two positions changes with respect to the previous two
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
        by checking if the difference of the next two positions changes with respect to the previous two
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


#################################################################################################################
# GLOBAL VARIABLES
#################################################################################################################
#used to crop the unnecessary parts of the arena
row_margin_top = 0
add_margin = 15
row_margin_bottom = 48
col_margin_left = 2
col_margin_right = 15
src_img = 0




#shapes,colors:used to store the information regarding the properties of objects present in the arena
#shapes: stores the objects present in the location(index)-> 0:obstacle 1:circle 2:square 3:triangle
shapes = []
#colors: stores the color values->0:red 1:green 2:blue
colors=[]
#stores whether the working area objects are matched or not
matches_work_area = []
#centroid: stores the centroids of the entities in the arena
centroids = []
#contour_areas: stores the contour areas of the entities in the arena
contour_areas = []
#matches: stores the information of the matches formed by the doorway shapes with the working arena
matches = []


#contains the color values(hsv-color space) of red,green,blue colors
values=[]
values = [(120,109,76),(180,255,255),(30,93,29),(113,255,129),(30,66,80),(113,211,255)]#(obtained by thresholding)



##################################################################################################################
# MAIN CODE STARTS HERE
##################################################################################################################   

#initialisation
#cap: used to capture images for the entire program
cap = cv2.VideoCapture(1)

#resetting the arrays to "-1"(-1 signifies that it is null)
#stores from 0 to 54 but we use 1 to 54 w.r.t position
for x in range(55):
    shapes.append(-1)
    colors.append(-1)
    centroids.append(-1)
    contour_areas.append(-1)
    matches_work_area.append(-1)

for x in range(7):
    matches.append(-1)  

#captures the image of the arena for further processing(capturing more number of frames to empty the camera buffer)
z = 50
while(z>0):
    _,src_img_color = cap.read()
    #cv2.imshow('input',src_img_color)
    cv2.waitKey(10)
    z = z - 1

#obtaining dimensions of image
rows,cols,_ = src_img_color.shape

#changing color space from RBG to Gray scale image
img = cv2.cvtColor(src_img_color,cv2.COLOR_BGR2GRAY)

#otsu binarization: to detect the shapes
_,thresh_otsu = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#binary image invertion
thresh_inv = cv2.bitwise_not(thresh_otsu)
cv2.imshow('thresh',thresh_inv)


#cropping the unnecessary portion of the arena (after otsu binarization)
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
        #skipping small unnecessary areas formed due to noise
        if cv2.contourArea(contours[no])<60:
            continue


        try:
            #finding centroid(using moments-contours)
            M = cv2.moments(contours[no])
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])

            #finding row number and column number
            r,c = getCoord(pos)

            cx = cx + (c-1)*(cols - col_margin_left - col_margin_right)/9.0
            cy = cy + (r-1)*(rows - row_margin_top - row_margin_bottom)/6.0

            #typecasting centroids to integer if the values comes out to be of float type
            cx = int(cx)
            cy = int(cy)

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
            #rectangle(area ratio > 0.85)
            if(area_ratio >0.85):
                print str(pos)+':rectangle\t'+'area ratio:'+str(area_ratio)+'\tcontour area: '+str(cv2.contourArea(contours[no]))
                shapes[pos] = 2
                contour_areas[pos] = cv2.contourArea(contours[no])
                centroids[pos] = (cx,cy)
            #circle(area ratio between 0.65 and 0.85)
            elif(area_ratio > 0.65 and area_ratio <= 0.85):
                print str(pos)+':circle\t'+'area ratio:'+str(area_ratio)+'\tcontour area: '+str(cv2.contourArea(contours[no]))
                shapes[pos] = 1
                contour_areas[pos] = cv2.contourArea(contours[no])
                centroids[pos] = (cx,cy)
            #triangle(area ratio between 0.65 and 0.30)
            elif(area_ratio <= 0.65 and area_ratio > 0.30):
                print str(pos)+':triangle\t'+'area ratio:'+str(area_ratio)+'\tcontour area: '+str(cv2.contourArea(contours[no]))
                shapes[pos] = 3
                contour_areas[pos] = cv2.contourArea(contours[no])
                centroids[pos] = (cx,cy)

         
#blurring the source image and changing color space to HSV(for color detection)
blur_img = cv2.bilateralFilter(src_img_color,5,50,50)
blur_img = cv2.medianBlur(blur_img,5)
img = cv2.cvtColor(blur_img,cv2.COLOR_BGR2HSV)

# COLOR detection(RGB)
#red:0, green:1, blue:2(values are stored in colors)
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

        #stores the color values in the 'colors' list only if there was an object detected earlier
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
#matching the doorway shapes
for x in (1,10,19,28,37,46):
    #matching with working arena
    for y in range(1,55):
        #plotting the position numbers on the image(for user visual friendliness)
        ctr = getxy(y,src_img_color)
        cv2.putText(src_img_color,str(y),(ctr[0],ctr[1]),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,0.5,(255,255,255),2)
        #matching the properties of the entities i.e shape and color
        if( x != y and shapes[x] != -1 and colors[x]!=-1 and shapes[x] == shapes[y] and colors[x] == colors[y] and matches_work_area[y] < 0):
            #The matched objects should be of same size i.e difference in contour areas should be very small
            if(y%9 != 1 and abs(contour_areas[y] - contour_areas[x]) < 60):
                #if the doorway object has one match in working area
                if(matches[(x/9)+1] == -1):
                    matches[(x/9) + 1] = y
                #if the doorway object has more than one match in the working area
                #In this case we will be matching only that object in the working arena which is closer to the doorway shape and the other object is left unmatched 
                else:
                    #finding which object of the two are closer to the doorway shape
                    match_new = centroids[y]
                    match_old = centroids[matches[(x/9)+1]]
                    match_shape = centroids[x]
                    #finding the distances between the doorway shape and the objects being matched
                    diff_new = (match_shape[0]-match_new[0])*(match_shape[0]-match_new[0]) + (match_shape[1]-match_new[1])*(match_shape[1]-match_new[1])
                    diff_old = (match_shape[0]-match_old[0])*(match_shape[0]-match_old[0]) + (match_shape[1]-match_old[1])*(match_shape[1]-match_old[1])
                    #printing the differences on the monitor
                    print 'diff_new: '+str(diff_new)+'\tdiff_old: '+str(diff_old)
                    #if the new objects if closer than the previous match
                    if(diff_new < diff_old):
                        matches[(x/9)+1] = y

                print str((y,x))
    #setting the flag(i.e it is matched and is not available for further matching) - object in the working area is mathced
    matches_work_area[matches[(x/9)+1]] = 1

#forming the match_pairs list which stores(converts) the match pairs in the form of tuples(since matches list is stored as an array)
match_pairs = []
for x in range(1,7):
    if(matches[x] != -1):
        match_pairs.append([matches[x],9*(x-1)+1])

#altering the matches of the door area shapes
#if there are two or more shapes in the door area that are identical
#Then the matches formed are exchanged such that the matches should form shortest distance with the pair it forms
#comparing the door area shapes
for x in range(len(match_pairs)-1):
    for y in range(x+1,len(match_pairs)):
        #checking if the doorway shapes are identical(with respect to the properties)
        if(shapes[match_pairs[x][1]] == shapes[match_pairs[y][1]] and colors[match_pairs[x][1]] == colors[match_pairs[y][1]]):
            p1_x = centroids[match_pairs[x][1]]
            p1_y = centroids[match_pairs[x][0]]
            p2_x = centroids[match_pairs[y][1]]
            p2_y = centroids[match_pairs[y][0]]
            
            #finding the distance between the pairs formed
            d1 = (p1_x[0]-p1_y[0])*(p1_x[0]-p1_y[0]) + (p1_x[1]-p1_y[1])*(p1_x[1]-p1_y[1])
            d2 = (p2_x[0]-p2_y[0])*(p2_x[0]-p2_y[0]) + (p2_x[1]-p2_y[1])*(p2_x[1]-p2_y[1])
            #sum of distance of the combination that currently exists
            sum_comb = d1 + d2
            #find the distance between the pairs if the matches were exchanged
            d1 = (p1_x[0]-p2_y[0])*(p1_x[0]-p2_y[0]) + (p1_x[1]-p2_y[1])*(p1_x[1]-p2_y[1])
            d2 = (p2_x[0]-p1_y[0])*(p2_x[0]-p1_y[0]) + (p2_x[1]-p1_y[1])*(p2_x[1]-p1_y[1])

            #sum of distance of the combination if the matches were exchanged
            sum_comb_swap = d1 + d2
            #displaying the result on the monitor
            print 'sum_comb: '+str(sum_comb)
            print 'sum_comb_swap: '+str(sum_comb_swap)
            #if exchange turns out to be the better one then swap the matches formed
            if(sum_comb_swap <= sum_comb):
                temp_match = match_pairs[y][0]
                print temp_match
                match_pairs[y][0] = match_pairs[x][0]
                match_pairs[x][0] = temp_match


#plotting the lines on the source image showing the matches found with the door arena shapes(for user visualisation)
for x in match_pairs:
    cv2.line(src_img_color,getxy(x[0],src_img_color),getxy(x[1],src_img_color),(255,255,255),3)

#determines in which order the working arena objects are to be picked up
sorted_match_pairs = []
#picking objects from top to bottom horizontally in each row
for pos in range(1,55):
    if(pos%9 != 1):
        for obj in match_pairs:
            if(obj[0] == pos):
                sorted_match_pairs.append(obj)

#reassigning the sorted list in the match_pairs
match_pairs = sorted_match_pairs
#displaying the matched pairs on the monitor(user readability)
print 'match pairs '+str(match_pairs)

cv2.imshow('matches',src_img_color)

#destroying other windows
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
ser_delay = 20              
#add_delay: additional delay to be induced if required
add_delay = 0
#soft_flag: when set rotates the robot only in soft rotate mode
soft_flag = 0

#lifts the hand of the robot in order to avoid the obstacles(only at begining of the bot movement)
comm.send_data('i');cv2.waitKey(100)
comm.send_data('o');cv2.waitKey(100)
 

#obstacles: contains the positions of the objects and obstacles in the arena through which bot can't traverse
obstacles = []              
#considers the objects and obstacles as obstacles with respect to the traversal of robot
for x in range(1,55):
    if(shapes[x] != -1):
        obstacles.append(x)
print 'obstacles: '+str(obstacles)

#next_pos_trav: stores the position where the bot would be present next         
next_pos_trav = 23  #initially the bot is present in the C-5 location

#invokes the algo_mod to set the objects positions
algo_mod.set_objects_positions(obstacles) #sets the positions of objects in the shortest path algorithm


#threshold values
#threshold angle(tolerance in the angle made by the robot with the destination)
thresh_ang = 4
#threshold distances (the distance which can be left between the robot and the destination after reaching closer to the destination)
thresh_dis_far = 2000       
thresh_dis_near = 1000     

#forward and backward colors of the bot(HSV-color space), obtained by thresholding
forward_values = ((127,83,179),(180,125,255))
backward_values = ((3,89,181),(15,141,255))


#directions for the traversal of the bot
#for each pair of the working area object and doorway shape
for obj in match_pairs:
    #zeta = 0 for traveral to the source(working area object) and zeta = 1 for traversal to the destination(door way)
    for zeta in range(2):  
        #finding route between the source and the destination
        if(zeta == 0):
            #finding the route between current position and source
            route_planned = algo_mod.find_route(next_pos_trav,obj[0],1,1)
            route_planned = find_critical_pts(route_planned)
            print 'routing between ' + str(next_pos_trav)+' ,'+str(obj[0])
            print 'routed: '+str(route_planned)
        else:
            #finding the route between object to the corresponding doorway shape
            print 'routing between ' + str(obj[0])+' ,'+str(obj[1])
            route_planned = algo_mod.find_route(obj[0],obj[1],1,1)
            print 'raw_route '+str(route_planned)
            route_planned = find_critical_pts(route_planned)
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


        #traversing through each point in the route
        for index in range(len(route_planned)):
            #sets the threshold distance(the threshold distance will be far when the destination is a object or doorway shape)
            if(route_planned[index] == obj[0] or route_planned[index] == obj[1]):
                thresh_dis_far = 6500      
                thresh_dis_near = 3700
                soft_flag = 0
            #sets the threshold distance(the distance will be nearer when the destination is an empty location)
            else:
                thresh_dis_far = 1900       
                thresh_dis_near = 1000
            
            #finds the coordinates of the destination point
            dest = getxy(route_planned[index],capz)
            

            #replaces the coordinates of the block with the coordinates of the shape or object if the destination to be reached is an object or doorway shape
            if(route_planned[index] == obj[0]):
                print 'dest '+str(dest)+' ,centroids '+ str(centroids[obj[0]])
                dest = centroids[obj[0]]
                print 'after dest '+str(dest)+' ,centroids '+ str(centroids[obj[0]])
            elif(route_planned[index] == obj[1]):
                dest = centroids[obj[1]]

            #runs infintely untill the intermediate desination is reached
            while(True):
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
                    #as robot can't rotate angle less than 5 degrees, we are rotating 8 degrees when angle is less than 5 degrees
                    if( abs(angle) <= 5):
                        if(angle > 0):
                            angle  = 8
                        elif(angle < 0):
                            angle = -8
                    #if it has to rotate a greater area: then use sharp rotate
                    if( abs(angle) > 100):
                        move_forward(150)
                        cv2.waitKey(150)
                        rotate(angle)
                        soft_flag = 1
                    #if it has to rotate smaller angle then: soft rotate (also when it is at border soft rotate is prefered)
                    elif(soft_flag == 1 and (not atBorder)):
                        if(distance > 5500):
                            soft_rotate(angle)
                        else:
                            move_forward(150)
                            cv2.waitKey(150)
                            rotate(angle)

                    else:
                        rotate(angle)
                        soft_flag = 1
                    
                #if the bot reached the destination adjust the angle and break the loop i.e to the next object
                elif(distance < thresh_dis_near):
                    print 'REACHED INNER REGION'
                    #checks if there need to be a slight correction in the angle and then do the actions
                    if(abs(angle) > thresh_ang):
                        if(soft_flag == 1):
                            soft_rotate(angle)
                        else:
                            rotate(angle)
                            soft_flag = 1
                    #if the bot reaches the object to be picked up
                    if(zeta == 0 and route_planned[index] == obj[0]):
                        cv2.waitKey(100);
                        #picking up the object
                        comm.send_data('X');cv2.waitKey(2100)
                        move_forward(400)
                        cv2.waitKey(300)#push forward a bit to enter into the block 
                        
                        soft_flag = 0
                        #setting that location as free i.e bot can now traverse through it
                        algo_mod.set_free_loc(obj[0])
                        algo_mod.set_free_loc(next_pos_trav)
                        break
                    #if the destination is the door way shape then
                    elif(zeta == 1 and route_planned[index] == obj[1]):
                        cv2.waitKey(10);
                        #dropping down the object
                        comm.send_data('I');cv2.waitKey(2100)
                        #moves backward a bit after deposition of the object in doorway
                        move_backward(250)
                        print 'set free loc '+str(obj[0])
                        
                        #setting that location as free i.e bot can now traverse through it
                        algo_mod.set_free_loc(obj[0])
                        algo_mod.set_free_loc(next_pos_trav)

                        #sets the next postion to traverse as neighbouring position to the current previous doorway shape
                        next_pos_trav = obj[1]+1
                        soft_flag = 0
                        break
                    #breaks out of the loop i.e goes for the next destination
                    break

                #whent the bot is between near and far region
                elif(distance > thresh_dis_near and distance < thresh_dis_far):
                    print '\t\t\t\t FORWARD MID'
                    move_forward(150)
                #whent the bot is far away from the destination
                elif(distance > thresh_dis_far):
                    print '\t\t\t\t MOVING:'+str(distance)
                    move(distance)

#final buzzer after completion of task for 7 seconds(but only 5 seconds is required)
comm.send_data('O');cv2.waitKey(7000)
comm.send_data('C');cv2.waitKey(100)


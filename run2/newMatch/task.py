#arena: A-F(1-6),1-9

#position of the points in the arena: '1' based index
#shapes: stores the objects present in the location(index)-> 0:obstacle 1:circle 2:square 3:triangle
#colors: stores the color values->0:red 1:green 2:blue

import cv2
import numpy as np
import cv2.cv as cv
import math
import sys
import time

import comm
import algo_mod
import angle_mod




#empty function(used for trackbar)
def nothing(x):
    pass

#soft rotates the robot by the angle specified
def soft_rotate(ang):
    global ser_delay,add_delay
    
    time_delay = abs(ang * (6230/360.0))
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
    if(abs(ang) < 10 ):
        time_delay = time_delay + 75
    if(time_delay != 0):
        cv2.waitKey(time_delay+add_delay)
    else:
        cv2.waitKey(100)



#hard rotates the bot by the angle specified
def rotate(ang):
    global ser_delay,add_delay

    time_delay = abs(ang * (3700/360.0))
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

def move(dis_px):
    global ser_delay,add_delay

    if(dis_px > 150000):
        dis_cm = dis_px*(6/5041.0)#25
        dis_cm = int(dis_cm)
    elif(dis_px < 150000 and dis_px >= 100000 ):
        dis_cm = dis_px*(10/5041.0)#25
        dis_cm = int(dis_cm)
    
    elif(dis_px <= 100000 and dis_px > 25000):
        dis_cm = dis_px *(18/5041.0)#45
        dis_cm = int(dis_cm)

    elif(dis_px <= 25000 and dis_px > 15000):
        dis_cm = dis_px *(25/5041.0)#45
        dis_cm = int(dis_cm)
    elif(dis_px <= 15000):
        dis_cm = dis_px *(28/5041.0)#45
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
        cv2.waitKey(t_delay+add_delay)

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
            if cv2.contourArea(ctrs[no])>100:
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

#moves the bot forward
def move_forward(time_delay):
    comm.send_data('8')
    cv2.waitKey(time_delay)
    comm.send_data('5')
    cv2.waitKey(75)

#moves the bot backward
def move_backward(time_delay):
    comm.send_data('2')
    cv2.waitKey(time_delay)
    comm.send_data('5')
    cv2.waitKey(75)


#resets the pwm of the bot to 255
def pwm_reset():
    global ser_delay
    comm.send_data('<v');cv2.waitKey(ser_delay)
    comm.send_data('25');cv2.waitKey(ser_delay)
    comm.send_data('5>');cv2.waitKey(ser_delay)

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

def getPositionFromCoord(point):
    r = point[0]
    c = point[1]
    return int(c+(r-1)*9)

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

def getCoord(pos):
    c = pos%9
    if(c == 0):
        c = 9
        r = pos/9
        return (r,c)
    r = (pos/9) +1
    return (r,c)

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

    #error retification(due to the slant view from camera)
    x = x+ 0.01*x
    y = y+ 0.01*y

    x = int(x)
    y = int(y)

    #top row
    if( pos >=1 and pos <=9):
        y = y-23
    #bottom row
    elif( pos >= 46 and pos <= 54 ):
        y = y+10
    
    #second column
    if( pos % 9 == 2):
        x = x - 15
    
    #last column
    if( pos % 9 == 0):
        x = x + 15
    return (x,y)

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

def find_critical_pts_mod(route):
    count = 0
    target_pts = []
    diff = 99999
    temp_diff = 99999
    target_pts.append(route[0])
    for i in range(1,len(route)):
        temp_diff = route[i] - route[i-1]
        if(diff != 99999):
            if(diff != temp_diff or count == 1):
                target_pts.append(route[i-1])
                diff = temp_diff
                count = 0
            else:
                count = count+1
        diff = temp_diff
    target_pts.append(route[-1])
    return target_pts

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
row_margin_top = 18
row_margin_bottom = 42
col_margin_left = 2
col_margin_right = 8
src_img = 0


#used to store the information regarding the properties of objects present in the arena
shapes = []
sizes=[]
colors=[]
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
values = [(113,63,147),(180,255,255),(66,63,25),(99,234,121),(75,149,84),(121,234,164)]#evng3





##################################################################################################################
# MAIN CODE STARTS HERE
##################################################################################################################   

#initialisation
cap = cv2.VideoCapture(1)

#resetting the arrays to "-1"
#stores from 0 to 54 but we use 1 to 54 w.r.t position
for x in range(55):
    shapes.append(-1)
    sizes.append(-1)
    colors.append(-1)
    centroids.append(-1)
    contour_areas.append(-1)
for x in range(7):
    matches.append(-1)  

#captures the image of the arena for further processing
z = 50
while(z>0):
    _,src_img_color = cap.read()
    cv2.imshow('input',src_img_color)
    cv2.waitKey(10)
    z = z - 1


rows,cols,_ = src_img_color.shape
src_img_color = src_img_color[row_margin_top:rows-row_margin_bottom,col_margin_left:cols-col_margin_right]
src_img = cv2.cvtColor(src_img_color,cv2.COLOR_BGR2GRAY)


cv2.namedWindow('Parameters',cv2.WINDOW_AUTOSIZE)
cv2.createTrackbar('neigh','Parameters',16,40,nothing)
cv2.createTrackbar('blur','Parameters',19,30,nothing)

neigh_val = 65

while(True):
    if (cv2.waitKey(100) & 0xFF == ord('q')):
        break
    neigh_val = cv2.getTrackbarPos('neigh','Parameters')
    blur_val = cv2.getTrackbarPos('blur','Parameters')


    if(neigh_val == 0):
        neigh_val = 1

    blur_img  = cv2.bilateralFilter(src_img,blur_val,75,75)
    blur_img  = cv2.medianBlur(blur_img,5)

    #rows,cols = blur_img.shape
    #blur_img = blur_img[row_margin_top:rows-row_margin_bottom,col_margin:cols-col_margin]
    
    adap_thresh = cv2.adaptiveThreshold(blur_img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,2*neigh_val+1,3)
    thresh_inv  = cv2.bitwise_not(adap_thresh)

    cv2.imshow('blur_img',blur_img)
    cv2.imshow('adaptive',thresh_inv)


blur_img  = cv2.bilateralFilter(src_img,blur_val,75,75)
blur_img  = cv2.medianBlur(blur_img,5)
rows,cols = blur_img.shape


for pos in range(1,55):

    if(pos == 23):
        continue

    roi_img = getROI(blur_img,pos)
    
    adap_thresh = cv2.adaptiveThreshold(roi_img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,(2*neigh_val+1),3)
    thresh_inv  = cv2.bitwise_not(adap_thresh)

    cv2.imshow("Inverted",thresh_inv)

    contours,hierachy = cv2.findContours(thresh_inv,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    img_temp = np.zeros(src_img.shape, np.uint8)

    for no in range(len(contours)):
        #print cv2.contourArea(contours[no])
        if cv2.contourArea(contours[no])<50:
            continue

        #centroid
        M = cv2.moments(contours[no])
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])

        #min area rectangle
        rect = cv2.minAreaRect(contours[no])
        box = cv2.cv.BoxPoints(rect)
        box = np.int0(box)

        try:
            #finding the ratio of areas
            area_ratio = cv2.contourArea(contours[no])/cv2.contourArea(box)
        except ZeroDivisionError:
            continue
        print 

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
        elif(area_ratio < 0.65 and area_ratio > 0.30):
            print str(pos)+':triangle\t'+'area ratio:'+str(area_ratio)+'\tcontour area: '+str(cv2.contourArea(contours[no]))
            shapes[pos] = 3
            contour_areas[pos] = cv2.contourArea(contours[no])
            centroids[pos] = (cx,cy)
         
        #cv2.waitKey(0)




cv2.waitKey(0)
cv2.destroyAllWindows()











#cropping the source image
blur_img = cv2.bilateralFilter(src_img_color,5,50,50)
blur_img = cv2.medianBlur(blur_img,5)
img = cv2.cvtColor(blur_img,cv2.COLOR_BGR2HSV)

# COLOR detection(RGB)
#red:0, green:1, blue:2
for x in range(3):

    cv2.waitKey(0)
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

        if(x == 0 and cv2.contourArea(box) > 500 and shapes[position] == -1):
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
#shapes in doorway
for x in (1,10,19,28,37,46):#make the values -1
    #objects in the working area
    for y in range(1,55):
        #ctr: stores the centroid of the object currently inspected
        ctr = getxy(y,src_img_color)
        cv2.putText(src_img_color,str(y),(ctr[0],ctr[1]),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,0.5,(255,255,255),2)
        #if the properties(shape,color) of the shape in the doorway match with the object in the working area then
        if( x != y and shapes[x] != -1 and colors[x]!=-1 and shapes[x] == shapes[y] and colors[x] == colors[y]):
            #making sure that the objects are of same size using the concept that the difference in contour areas fall between ranges
            if(y%9 != 1 and abs(contour_areas[y] - contour_areas[x]) < 60):
                #matches.append((y,x))
                if(matches[(x/9)+1] == -1):
                    matches[(x/9) + 1] = y
                else:
                    r_new = y/9
                    r_old = matches[(x/9)+1]/9
                    r_x = x/9
                    diff_new = abs(r_x - r_new)
                    diff_old = abs(r_x - r_old)
                    print 'diff_new: '+str(diff_new)+'\tdiff_old: '+str(diff_old)
                    if(diff_new < diff_old):
                        matches[(x/9)+1] = y
                    
                '''
                else:
                    print 'x:'+str(contour_areas[x])+'\ty'+str(contour_areas[y])
                    diff1 = abs(contour_areas[x] - contour_areas[y])
                    print diff1
                    print 'x:'+str(contour_areas[x])+'\ty'+str(contour_areas[matches[(x/9)+1]])
                    diff2 = abs(contour_areas[x] - contour_areas[matches[(x/9)+1]])
                    print diff2

                    if(diff1 < diff2):
                        matches[(x/9)+1] = y
                        pass
                '''

                print str((y,x))

#plotting the lines on the source image showing the matches found with the door arena shapes
for x in range(1,7):
    if(matches[x] != -1):
        cv2.line(src_img_color,getxy(9*(x-1)+1,src_img_color),getxy(matches[x],src_img_color),(255,255,255),3)

#sorting the matched objects in order to pickup the objects that are closer to the door area
match_pairs = []
for x in range(1,7):
    if(matches[x] != -1):
        match_pairs.append((matches[x],9*(x-1)+1))

sorted_match_pairs = []

for ind in range(2,9):
    for obj in match_pairs:
        if(obj[0] % 9 == ind):
            sorted_match_pairs.append(obj)
for obj in match_pairs:
    if(obj[0] % 9 == 0):
        sorted_match_pairs.append(obj)
match_pairs = sorted_match_pairs

print 'match pairs '+str(match_pairs)

cv2.imshow('matches',src_img_color)


#Asking the user to continue further if the matches are correct
print 'DO YOU WANT TO CONTINUE'

if(cv2.waitKey(0) & 0xFF == ord('q')):
    sys.exit()

cv2.destroyWindow('contours0')
cv2.destroyWindow('otsu_roi')
cv2.destroyWindow('thresh_inv')
cv2.destroyWindow('contours1')
cv2.destroyWindow('contours2')


####################################################################################################################
# BOT MOVEMENT
####################################################################################################################

cam_delay = 4               #delay that is induced between successive captures from the image
no_of_frames = 14           #no of frames that have to be captured in order to empty the buffer
ser_delay = 50              #delay between successive bytes when communicating with xbee
add_delay = 0
soft_flag = 0

comm.send_data('i');cv2.waitKey(100)
comm.send_data('o');cv2.waitKey(100)
 



#has the positions of the objects and obstacles in the arena through which bot can't traverse
obstacles = []              
for x in range(1,55):
    if(shapes[x] != -1):
        obstacles.append(x)
print 'obstacles: '+str(obstacles)

#saves the position where the bot currently is present         
next_pos_trav = 23

algo_mod.set_objects_positions(obstacles) #sets the positions of objects in the shortest path algorithm

#threshold values for far region to the destination
thresh_ang = 6
thresh_dis_far = 2000       #3000
thresh_dis_near = 1000       #600

#forward and backward colors of the bot
forward_values = ((117,99,117),(130,199,183))
backward_values = ((0,65,170),(89,164,250))


#directions for the traversal of the bot
for obj in match_pairs:
    #zeta = 0 for traveral to the source(working area object) and zeta = 1 for traversal to the destination(door way)
    for zeta in range(2):  
        
        #finding route between the source and the destination
        if(zeta == 0):
            route_planned = algo_mod.find_route(next_pos_trav,obj[0],1,1)
            route_planned = find_critical_pts_mod(route_planned)
            print 'routing between ' + str(next_pos_trav)+' ,'+str(obj[0])
            print 'routed: '+str(route_planned)
        else:
            route_planned = algo_mod.find_route(obj[0],obj[1],1,1)
            print 'raw_route '+str(route_planned)
            route_planned = find_critical_pts_mod(route_planned)
            print 'routing between ' + str(obj[0])+' ,'+str(obj[1])
            print 'routed: '+str(route_planned)

        z = no_of_frames
        capz = 0
        while(z>0):
            _,capz = cap.read()
            cv2.waitKey(cam_delay)
            z = z-1
        
        rows,cols,_ = capz.shape
        capz = capz[row_margin_top:rows-row_margin_bottom,col_margin_left:cols - col_margin_right]
        
        for i in range(1,55):
            cv2.circle(capz,getxy(i,capz),1,(0,0,255),cv2.CV_AA)
        cv2.imshow('centroids',capz)

        for index in range(len(route_planned)):

            if(route_planned[index] == obj[0] or route_planned[index] == obj[1]):
                thresh_dis_far = 6500       #3000
                thresh_dis_near = 3700
                soft_flag = 0
            else:
                thresh_dis_far = 1900       #3000
                thresh_dis_near = 1000
        
            #bf,bc,img_temp = find_bot(capz,forward_values,backward_values)
            dest = getxy(route_planned[index],capz)

            if(route_planned[index] == obj[0]):
                print 'dest '+str(dest)+' ,centroids '+ str(centroids[obj[0]])
                dest = centroids[obj[0]]
                print 'after dest '+str(dest)+' ,centroids '+ str(centroids[obj[0]])

            elif(route_planned[index] == obj[1]):
                dest = centroids[obj[1]]

        
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
                cv2.imshow('botc',capz)

                #finds bot location
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
                    if( abs(angle) < 5):
                        if(angle > 0):
                            angle  = 5
                        elif(angle < 0):
                            angle = -5
                    if( abs(angle) > 100):
                        move_forward(150)
                        cv2.waitKey(300)
                        rotate(angle)
                        soft_flag = 1
                    elif(soft_flag == 1 and (not atBorder)):
                        if(distance > 5500 and curr_pos %9 != 2):
                            soft_rotate(angle)
                        else:
                            move_forward(150)
                            cv2.waitKey(300)
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
                        comm.send_data('x');cv2.waitKey(2000)
                        comm.send_data('c');cv2.waitKey(1000)
                        comm.send_data('i');cv2.waitKey(2000)
                        #buzzer
                        comm.send_data('O');cv2.waitKey(100)
                        comm.send_data('C');cv2.waitKey(100)
                        comm.send_data('O');cv2.waitKey(100)
                        comm.send_data('C');cv2.waitKey(100)

                        move_forward(325)
                        cv2.waitKey(1000)#push forward
                        
                        soft_flag = 0
                        break
                    elif(zeta == 1 and route_planned[index] == obj[1]):
                        cv2.waitKey(10);
                        #dropping down the object
                        comm.send_data('x');cv2.waitKey(2000)
                        comm.send_data('o');cv2.waitKey(1000)
                        comm.send_data('i');cv2.waitKey(2000)
                        
                        move_backward(250)
                        print 'set free loc '+str(obj[0])
                        algo_mod.set_free_loc(obj[0])
                        
                        #buzzer
                        comm.send_data('O');cv2.waitKey(100)
                        comm.send_data('C');cv2.waitKey(100)
                        comm.send_data('O');cv2.waitKey(100)
                        comm.send_data('C');cv2.waitKey(100)
                       
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
comm.send_data('O');cv2.waitKey(1000)
comm.send_data('C');cv2.waitKey(100)
comm.send_data('O');cv2.waitKey(1000)
comm.send_data('C');cv2.waitKey(100)







#c:center f:forward

import ang
import cv2
import numpy as np
#import py_serial

def nothing(x):
    pass

def move_right():
    print 'right'
    py_serial.send_data('6')
    cv2.waitKey(50)
    py_serial.send_data('5')
   
def move_left():
    print 'left'
    py_serial.send_data('4')
    cv2.waitKey(50)
    py_serial.send_data('5')
   

def move_forward():
    print 'forward'
    py_serial.send_data('8')
    cv2.waitKey(50)
    py_serial.send_data('5')
   
def move_backward():
    print 'back'
    py_serial.send_data('8')
    cv2.waitKey(50)
    py_serial.send_data('5')
  

def find_bot(img_cap):
    global values
    img_temp = np.ones((400,400),np.uint8)#empty image to display the result    
    for x in range(1,3):
        lower_values = values[x][0]
        higher_values = values[x][1]
        
        #color filtering
        mask = cv2.inRange(img_cap,lower_values,higher_values)
        #opening
        mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
        mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
        #closing
        mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
        mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
        cv2.imshow('mask',mask)
        #finding contours of the thresholded image
        contours,hierachy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        for no in range(len(contours)):
            if cv2.contourArea(contours[no])<200:
                continue
            #centroid
            M = cv2.moments(contours[no])
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            if x==1:
                bot_f = (cx,cy)
                print bot_f
            if x==2:
                bot_c = ((cx+bot_f[0])/2,(bot_f[1]+cy)/2)
                print bot_c
                        
        #draw on the new image
        cv2.putText(img_temp,"pos"+str(x),(cx,cy),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1,(255,255,255),2)
        cv2.drawContours(img_temp, contours,-1, (255,255,255), 2)
        cv2.imshow("bot",img_temp)
    cv2.line(img_temp,bot_c,dest,(255),5)
    return bot_f,bot_c

#########################################################################

#global variables
bot_f = ()
bot_c = ()
dest = ()
distance = 99999
values = []
img_cap = 0


##########################################################################


#camera initialisation
cap = cv2.VideoCapture(1)


#initialisation

cv2.namedWindow('pallete',cv2.WINDOW_AUTOSIZE)
#cv2.imshow('input',src_img)
#cv2.imshow('blur',blur_img)

# create trackbars for color change
cv2.createTrackbar('low_h','pallete',0,180,nothing)
cv2.createTrackbar('low_s','pallete',0,255,nothing)
cv2.createTrackbar('low_v','pallete',0,255,nothing)
cv2.createTrackbar('high_h','pallete',180,180,nothing)
cv2.createTrackbar('high_s','pallete',255,255,nothing)
cv2.createTrackbar('high_v','pallete',255,255,nothing)


#loop for trackbar
for x in range(3):
    while(1):
        _,src_img = cap.read()
        img = cv2.imread('test_images/test19.jpg')
        blur_img = cv2.GaussianBlur(src_img,(5,5),0)
        cv2.imshow('frame',src_img)
        img = cv2.cvtColor(blur_img,cv2.COLOR_BGR2HSV)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print "obtained"+str(x)
            values.append((lower_values,higher_values))
            print lower_values
            print  higher_values
            #cv2.destroyAllWindows()
            break
        # get current positions of four trackbars
        low_h = cv2.getTrackbarPos('low_h','pallete')
        low_s = cv2.getTrackbarPos('low_s','pallete')
        low_v = cv2.getTrackbarPos('low_v','pallete')
        high_h = cv2.getTrackbarPos('high_h','pallete')
        high_s = cv2.getTrackbarPos('high_s','pallete')
        high_v = cv2.getTrackbarPos('high_v','pallete')
        
        #creating an array of values
        lower_values = np.array([low_h,low_s,low_v])
        higher_values = np.array([high_h,high_s,high_v])

        #color filtering
        mask = cv2.inRange(img,lower_values,higher_values)
        #opening
        mask = cv2.erode(mask,np.ones((2,2),np.uint8),iterations = 1)
        mask = cv2.dilate(mask,np.ones((2,2),np.uint8),iterations = 1)
        #closing
        mask = cv2.dilate(mask,np.ones((2,2),np.uint8),iterations = 1)
        mask = cv2.erode(mask,np.ones((2,2),np.uint8),iterations = 1)
        if (x==0):
            mask_x = mask
        cv2.imshow('mask',mask)

##########################################################################
#DRAW CONTOURS NOW
##########################################################################

#finding contours of the thresholded image
contours,hierachy = cv2.findContours(mask_x,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
img_temp = np.ones((400,400),np.uint8)#empty image to display the result
for no in range(len(contours)):
    if cv2.contourArea(contours[no])<200:
        continue
    #centroid
    M = cv2.moments(contours[no])
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    dest = (cx,cy)
                        
    #draw on the new image
    cv2.putText(img_temp,"dest",(cx,cy),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1,(255,255,255),2)
    cv2.drawContours(img_temp, contours,-1, (255,255,255), 2)
    cv2.imshow("dest",img_temp)
        

############################################################################
#MOVEMENT OF BOT
###########################################################################
while(True):
    cv2.waitKey(250)
    #captures img for finding bot
    _,img_cap = cap.read()
    cv2.imshow("output",img_cap)
    
    #function to return the coordinates of the bot
    bot_f,bot_c = find_bot(img_cap)
    angle = ang.between(bot_f,dest,bot_c)
    distance = (dest[0]-bot_c[0])*(dest[0]-bot_c[0]) + (dest[1]-bot_c[1])*(dest[1]-bot_c[1])
    print str(angle) +" , "+ str(distance)
    if(angle > 30 or angle < -30):
        if(angle>30):
            move_right()
            continue
        else:
            move_left()
            continue

    if(distance >800):
        move_forward()
        continue
    

cap.release()
cv2.imshow('frame',img)

cv2.waitKey(0)
cv2.destroyAllWindows()

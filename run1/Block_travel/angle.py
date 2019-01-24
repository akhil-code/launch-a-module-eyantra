import cv2
import numpy as np
import math

def get_point(event,x,y,flags,params):
    global blank_img,c,p1,p2,count
    if(event == cv2.EVENT_LBUTTONDBLCLK):
        if(count ==0):
            #mark centre
            c = (x,y)
            cv2.circle(blank_img,c,5,(255,255,255),-1)
            cv2.imshow('image',blank_img)
            count = 1
        elif(count == 1):
            #mark p1
            p1 = (x,y)
            cv2.line(blank_img,p1,c,(0,0,255),2,cv2.CV_AA)
            cv2.imshow('image',blank_img)
            count = 2
        elif(count == 2):
            #mark p2
            p2 = (x,y)
            cv2.line(blank_img,p2,c,(0,255,0),2,cv2.CV_AA)
            cv2.imshow('image',blank_img)
            count = 3
            #print angle_between(p1,p2,c)
            print 'src: '+str(angleof(p1,c))
            print 'dest: '+str(angleof(p2,c))
        elif(count == 3):
            blank_img = np.zeros((480,640,3), np.uint8)
            cv2.imshow('image',blank_img)
            count =0
 

def angleof(p,c):
    if(c[0] == p[0] and p[1] > c[1]):
        angle = 90
    elif(c[0] == p[0] and p[1] < c[1]):
        angle = -90
    elif(c[1] == p[1] and p[0] > c[0]):
        angle = 0
    elif(c[1] == p[1] and p[0] < c[0]):
        angle = 180
    elif(p[0] > c[0] and p[1] > c[1]):
        #q4    
        m = (p[1]-c[1])/float((p[0]-c[0]))
        angle = math.atan(m)
        angle = math.degrees(angle)
    elif(p[0] > c[0] and p[1] < c[1]):
        #q1    
        m = (p[1]-c[1])/float((p[0]-c[0]))
        angle = math.atan(m)
        angle = math.degrees(angle)
    elif(p[0] < c[0] and p[1] < c[1]):
        #q2    
        m = (p[1]-c[1])/float((p[0]-c[0]))
        angle = math.atan(m)
        angle = math.degrees(angle)
        angle = angle-180
    elif(p[0] < c[0] and p[1] > c[1]):
        #q3    
        m = (p[1]-c[1])/float((p[0]-c[0]))
        angle = math.atan(m)
        angle = math.degrees(angle)
        angle = angle+180

    return angle

#p1:source p2:dest c:centre
def angle_between(p1,p2,c):
    angle1 = angleof(p1,c)
    angle2 = angleof(p2,c)

    angle = angle2-angle1
    if(abs(angle) > 180):
        if(angle < 0):
            angle = 360 - abs(angle)
        elif(angle > 0):
            angle = -(360 - angle)
    return angle



#############################################################################
blank_img = np.zeros((480,640,3), np.uint8)
count = 0

p1 = (0,0)
p2 = (0,0)
c = (0,0)

cv2.imshow('image',blank_img)
cv2.setMouseCallback('image',get_point)
cv2.waitKey(0)
cv2.destroyAllWindows()

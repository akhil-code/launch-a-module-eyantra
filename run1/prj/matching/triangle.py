#equidistant
#contour area ratio (three points)

import cv2
import numpy as np
import tri_ang

def drawTriangle(p1,p2,p3,src_img):
    cv2.line(src_img,p1,p2,(255,255,255),1)
    cv2.line(src_img,p2,p3,(255,255,255),1)
    cv2.line(src_img,p3,p1,(255,255,255),1)

def isEquilateral(p1,p2,p3):
    d1 = (p1[0]-p2[0])*(p1[0]-p2[0]) + (p1[1]-p2[1])*(p1[1]-p2[1])
    d2 = (p2[0]-p3[0])*(p2[0]-p3[0]) + (p2[1]-p3[1])*(p2[1]-p3[1])
    d3 = (p1[0]-p3[0])*(p1[0]-p3[0]) + (p1[1]-p3[1])*(p1[1]-p3[1])

    #print (float(d1)/float(d2))
    #print (float(d2)/float(d3))
    #print (float(d3)/float(d1))

    minv = 0.7 
    maxv = 1.6
    if((float(d1)/float(d2))>minv and (float(d2)/float(d3))>minv and (float(d3)/float(d1))>minv):
        if((float(d1)/float(d2))<maxv and (float(d2)/float(d3))<maxv and (float(d3)/float(d1))<maxv):
            return True
    else:
        return False

#return ROI of the desired position
def getROI(src_img,pos):
    #finds dimensions of arena
    rows,cols,_ = src_img.shape
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
    #return roi of calculated pixels
    return src_img[rows_start:rows_end,cols_start:cols_end]

#####################################################################

#cap = cv2.VideoCapture(1)
src_img = 0
positions = []

while(1):
    #_,src_img = cap.read()
    src_img = cv2.imread('src.jpg')
    cv2.imshow('input',src_img)
    if(cv2.waitKey(100) & 0xFF == ord('q')):
       cv2.destroyAllWindows()
       break


#src_img = cv2.imread('test_images/test0.jpg')
for pos in range(1,55):
    points = []
    box = 0
    temp_img = getROI(src_img,pos)

    #finding corner points
    gray = cv2.cvtColor(temp_img,cv2.COLOR_BGR2GRAY)
    corners = cv2.goodFeaturesToTrack(gray,3,0.01,10)
    if(corners == None):
        continue
    print 'in pos: '+str(pos)
    corners = np.int0(corners)
    for i in corners:
        x,y = i.ravel()
        points.append((x,y))
        cv2.circle(temp_img,(x,y),3,255,-1)
    equi = isEquilateral(points[0],points[1],points[2])

    min_angle = 40
    max_angle = 80

    try:
        equi_angle = False
        angle1 =    abs(tri_ang.between(points[0],points[2],points[1]))
        angle2 =    abs(tri_ang.between(points[1],points[0],points[2]))
        angle3 =    abs(tri_ang.between(points[2],points[1],points[0]))
        print str(angle1)+' , '+str(angle2)+' , '+str(angle3)

        if( angle1< max_angle and angle2<max_angle and angle3<max_angle):
            if(angle1>min_angle and angle2>min_angle and angle3>min_angle):
                equi_angle = True

    except TypeError:
        continue    

    #finding contour area
    blank_img = np.zeros((100,100,3), np.uint8)
    drawTriangle(points[0],points[1],points[2],blank_img)

    blank_img = cv2.cvtColor(blank_img,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(blank_img,(0,0,10),(180,255,255))

    contours,hierachy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for no in range(len(contours)):
        if cv2.contourArea(contours[no])<20:
            continue

        #min area rectangle
        rect = cv2.minAreaRect(contours[no])
        box = cv2.cv.BoxPoints(rect)
        box = np.int0(box)

        #finding the ratio of areas
        area_ratio = cv2.contourArea(contours[no])/cv2.contourArea(box)
        break
    #print 'equi' + str(equi)
    #print 'area_ratio' + str(area_ratio)
    #print 'contour area: ' +str(cv2.contourArea(box))
    '''
    if( equi and area_ratio <0.8 and cv2.contourArea(box)<400):
        print 'True'
        positions.append(pos)
    else:
        print 'false'
    '''
    if(equi_angle and cv2.contourArea(box)<400):
        print 'true'
        positions.append(pos)
    else:
        print 'false'
    
        
    #cv2.imshow('frame',temp_img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

for x in positions:
    print x
cv2.imshow('input',src_img)
cv2.waitKey(0)
cv2.destroyAllWindows()


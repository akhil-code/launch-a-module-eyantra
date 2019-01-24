import cv2
import cv2.cv as cv
import numpy as np
import math

#finds to which block the coordinates belong to
def getPosition(pt,src_img):
    x = pt[0]
    y = pt[1]
    row,col = src_img.shape
    c = math.ceil(x/(col/9.0))
    r = math.ceil(y/(row/6.0))
    return (r,c)

def getPositionFromCoord(pt):
    r = pt[0]
    c = pt[1]
    return c+(r-1)*9

#return ROI of the desired position
def getROI(src_img,pos):
    #finds dimensions of arena
    rows,col,_ = src_img.shape
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
    temp_img =  src_img[rows_start:rows_end,cols_start:cols_end]
    return temp_img

img = cv2.imread('test_images/test0.jpg',0)
img = cv2.bilateralFilter(img,7,50,50)
#cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
circles = cv2.HoughCircles(img,cv.CV_HOUGH_GRADIENT,1,20,param1=50,param2=30,minRadius=2,maxRadius=10)

circles = np.uint16(np.around(circles))
for i in circles[0,:]:
    t =  getPosition((i[0],i[1]),img)
    print getPositionFromCoord(t)
    # draw the outer circle
    cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
    # draw the center of the circle
    #cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)

cv2.imshow('detected circles',img)
cv2.waitKey(0)
cv2.destroyAllWindows()



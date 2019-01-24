import cv2
import numpy as np

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

img = cv2.imread('test0.jpg')
img = getROI(img,28)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray,50,150,apertureSize = 3)
lines = cv2.HoughLines(edges,1,np.pi/180,12)
for rho,theta in lines[0]:
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 1000*(-b))
    y1 = int(y0 + 1000*(a))
    x2 = int(x0 - 1000*(-b))
    y2 = int(y0 - 1000*(a))
    cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)

cv2.imshow('frame',img)
cv2.waitKey(0)
cv2.destroyAllWindows()

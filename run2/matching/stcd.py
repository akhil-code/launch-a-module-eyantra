import numpy as np
import cv2

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
corners = cv2.goodFeaturesToTrack(gray,4,0.01,10)
corners = np.int0(corners)
print len(corners)
for i in corners:
    x,y = i.ravel()
    cv2.circle(img,(x,y),3,255,-1)
cv2.imshow('frame',img)
cv2.waitKey(0)
cv2.destroyAllWindows()

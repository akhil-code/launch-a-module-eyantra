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

filename = 'test0.jpg'

img = cv2.imread(filename)
img = getROI(img,28)
img = cv2.bilateralFilter(img,9,75,75)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
gray = np.float32(gray)

dst = cv2.cornerHarris(gray,2,3,0.04)
#result is dilated for marking the corners, not important
dst = cv2.dilate(dst,None)

# Threshold for an optimal value, it may vary depending on the image.
img[dst>0.1*dst.max()]=[0,0,255]
print 'length: '+str(len(dst))
print dst
cv2.imshow('dst',img)

cv2.waitKey(0)
cv2.destroyAllWindows()

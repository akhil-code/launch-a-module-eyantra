########################################################################################
# l = [p+sqrt(p*p - 4*a)]/4
# b = a/l;

########################################################################################



import cv2
import numpy as np
import math

def nothing(x):
    pass

#initialisation
cv2.namedWindow('pallete',cv2.WINDOW_AUTOSIZE)


# create trackbars for color change
cv2.createTrackbar('low_h','pallete',0,180,nothing)
cv2.createTrackbar('low_s','pallete',0,255,nothing)
cv2.createTrackbar('low_v','pallete',0,255,nothing)
cv2.createTrackbar('high_h','pallete',179,180,nothing)
cv2.createTrackbar('high_s','pallete',254,255,nothing)
cv2.createTrackbar('high_v','pallete',254,255,nothing)


#loop for trackbar
while(1):
    #_,src_img = cap.read()
    src_img = cv2.imread('test_images/test19.jpg')
    rows,columns,_ = src_img.shape
    blur_img = cv2.GaussianBlur(src_img,(5,5),0)
    img = cv2.cvtColor(blur_img,cv2.COLOR_BGR2HSV)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # get current positions of four trackbars
    low_h = cv2.getTrackbarPos('low_h','pallete')
    low_s = cv2.getTrackbarPos('low_s','pallete')
    low_v = cv2.getTrackbarPos('low_v','pallete')
    high_h = cv2.getTrackbarPos('high_h','pallete')
    high_s = cv2.getTrackbarPos('high_s','pallete')
    high_v = cv2.getTrackbarPos('high_v','pallete')
    lower_values = np.array([low_h,low_s,low_v])
    higher_values = np.array([high_h,high_s,high_v])

    #color filtering
    mask = cv2.inRange(img,(88,21,0),(163,255,125))
    #opening
    mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
    mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
    #closing
    mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
    mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)

    cv2.imshow('mask',mask)
    cv2.imshow('input',src_img)
    

#finding contours of the thresholded image
contours,hierachy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
img_temp = np.ones((rows,columns),np.uint8)#empty image to display the result

for no in range(len(contours)):
    if cv2.contourArea(contours[no])<100:
        continue
    
    
	#min area rectangle
    rect = cv2.minAreaRect(contours[no])
    box = cv2.cv.BoxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(img_temp, approx,-1, (255,255,255), 2)
    '''
    area = cv2.contourArea(box)
    perimeter = cv2.arcLength(box,True)
    length = (perimeter+math.sqrt(perimeter*perimeter - 4*area))/4.0
    breadth = area/length
    print "length: "+str(length)+"\tbreadth: "+str(breadth)
    '''

print count

cv2.imshow("contours",img_temp)                   

cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.waitKey(0);
cv2.destroyAllWindows();

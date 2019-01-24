import cv2
import numpy as np

def nothing(x):
    pass

#initialisation
#cap = cv2.VideoCapture(0)
cv2.namedWindow('pallete',cv2.WINDOW_AUTOSIZE)

#cv2.imshow('blur',blur_img)

# create trackbars for color change
cv2.createTrackbar('low_h','pallete',0,180,nothing)
cv2.createTrackbar('low_s','pallete',0,255,nothing)
cv2.createTrackbar('low_v','pallete',0,255,nothing)
cv2.createTrackbar('high_h','pallete',180,180,nothing)
cv2.createTrackbar('high_s','pallete',255,255,nothing)
cv2.createTrackbar('high_v','pallete',255,255,nothing)


#loop for trackbar
while(1):
    #_,src_img = cap.read()
    src_img = cv2.imread('test2.jpg')
    #rows,columns,_ = src_img.shape
    #gaussian noise: edge noise
    #blur_img = cv2.GaussianBlur(src_img,(5,5),0)
    #bilateralFilter: preserves edges
    blur_img = cv2.bilateralFilter(src_img,9,50,50)
    cv2.imshow('blur',blur_img)
    #median blur: salt and pepper noise
    #blur_img = cv2.medianBlur(src_img,5)
    img = cv2.cvtColor(src_img,cv2.COLOR_BGR2HSV)
    
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
    mask = cv2.inRange(img,lower_values,higher_values)
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
img_temp = np.ones((800,800),np.uint8)#empty image to display the result
#cv2.drawContours(img_temp, contours,-1, (255,255,255), 2)

for x in range(len(contours)):
    cnt = contours[x]
    hull = cv2.convexHull(cnt,returnPoints = True)

    pts = np.array(hull, np.int32)
    pts = pts.reshape((-1,1,2))
    cv2.polylines(img_temp,[pts],True,(255,255,255))

cv2.imshow('frame',img_temp)

cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.waitKey(0);
cv2.destroyAllWindows();

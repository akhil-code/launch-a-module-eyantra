import cv2
import numpy as np

def nothing(x):
    pass


img1 = cv2.imread('test0.jpg')


cv2.namedWindow('pallete',cv2.WINDOW_AUTOSIZE)
# create trackbars for color change
cv2.createTrackbar('low_h','pallete',0,180,nothing)
cv2.createTrackbar('low_s','pallete',0,255,nothing)
cv2.createTrackbar('low_v','pallete',0,255,nothing)
cv2.createTrackbar('high_h','pallete',180,180,nothing)
cv2.createTrackbar('high_s','pallete',255,255,nothing)
cv2.createTrackbar('high_v','pallete',255,255,nothing)


#loop for trackbar
while(1):
    src_img = img1
	#bilateralFilter: preserves edges
    blur_img = cv2.bilateralFilter(src_img,7,50,50)
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
    mask = cv2.inRange(img,lower_values,higher_values)
    #opening
    mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
    mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
    #closing
    mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
    mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)

    cv2.imshow('mask',mask)
    cv2.imshow('input',src_img)



coord = []
for x in range (2):
    coord.append((10,10))
img_temp = np.ones((800,800),np.uint8)#empty image to display the result

contours,hierarchy = cv2.findContours(mask,2,1)
for x in range(len(contours)):
    print 'contour area of '+str(x)+' : '+ str(cv2.contourArea(contours[x]))
    if (cv2.contourArea(contours[x])>8000 or cv2.contourArea(contours[x])<50):
        continue
    #centroid
    M = cv2.moments(contours[x])
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    #coord.append((cx,cy))
    coord[0] = (cx,cy)
    cv2.drawContours(img_temp, contours,-1, (255,255,255), 2)
    cv2.putText(img_temp,str(x),(cx,cy),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1,(255,255,255),2)
    for y in range(x+1,len(contours)):
        if (cv2.contourArea(contours[y])>8000 or cv2.contourArea(contours[y])<50):
            continue
        #centroid
        M = cv2.moments(contours[y])
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        #coord.append((cx,cy))
        coord[1] = (cx,cy)
        ret = cv2.matchShapes(contours[x],contours[y],1,0.0)
        if( ret < 0.01):
            print 'printed'
            cv2.line(img_temp,coord[0],coord[1],(255,255,255),2)
        print str(x)+" , "+str(y)+" : "+str(ret)

cv2.imshow("draw",img_temp)

cv2.waitKey(0)
cv2.destroyAllWindows()

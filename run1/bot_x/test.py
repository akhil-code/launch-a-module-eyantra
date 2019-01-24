################################################################################################

#step1: thresholding and forming a variable values containing the color values of all colors
#red(0),green(1),blue(2),margin(3),bot_f(4),bot_b(5)

#pre - step2: find the track dimensions

#step2: find the details of the objects
#       (apply contours and find the shapes and sizes of the objects)

#################################################################################################





import cv2
import numpy as np
#import ang
################################################################################################
#functions defined

def find_position():
    return 0

def find_bot(img_cap):
    global values
    img_temp = np.ones((400,400),np.uint8)#empty image to display the result    
    for x in (4,5):
        lower_values = values[x][0]
        higher_values = values[x][1]
        
        #color filtering
        mask = cv2.inRange(img_cap,lower_values,higher_values)
        #opening
        mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
        mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
        #closing
        mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
        mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
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
            if x==4:
                bot_f = (cx,cy)
                print bot_f
            if x==5:
                bot_c = ((cx+bot_f[0])/2,(bot_f[1]+cy)/2)
                print bot_c
                        
        #draw on the new image
        cv2.putText(img_temp,"pos"+str(x),(cx,cy),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1,(255,255,255),2)
        cv2.drawContours(img_temp, contours,-1, (255,255,255), 2)
        cv2.imshow("bot",img_temp)
    cv2.line(img_temp,bot_c,dest,(255),5)
    return bot_f,bot_c

################################################################################################



################################################################################################
#global variables

values = []         #stores values of colours
img_arena = []      #stores duplicate img of arena
details_objects = []#stores details of all the objects in the arena
################################################################################################





#camera initialisation
cap = cv2.VideoCapture(1)


#initialisation

# create trackbars for color change
cv2.namedWindow('pallete',cv2.WINDOW_AUTOSIZE)
cv2.createTrackbar('low_h','pallete',0,180,nothing)
cv2.createTrackbar('low_s','pallete',0,255,nothing)
cv2.createTrackbar('low_v','pallete',0,255,nothing)
cv2.createTrackbar('high_h','pallete',180,180,nothing)
cv2.createTrackbar('high_s','pallete',255,255,nothing)
cv2.createTrackbar('high_v','pallete',255,255,nothing)


#loop for trackbar
for x in range(6):
    while(1):
        #to stop the operation
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print "obtained"+str(x)
            values.append((lower_values,higher_values))#appends to the global variable values
            print lower_values
            print  higher_values
            img_arena = img                          #for further processing saving a duplicate img
            break

        _,src_img = cap.read()#capture image
        #img = cv2.imread('test_images/test19.jpg')
        blur_img = cv2.GaussianBlur(src_img,(5,5),0)#apply blur
        img = cv2.cvtColor(blur_img,cv2.COLOR_BGR2HSV)#converts rgb to hsv
        
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
        mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
        mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
        #closing
        mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
        mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
        cv2.imshow('mask',mask)


#obtaining the details of the objects in the arena
for x in range(3):

	#color filtering
	mask = cv2.inRange(img,values[x][0],values[x][1])
	#opening
	mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
	mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
	#closing
	mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
	mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)

	#finding contours of the thresholded image
	contours,hierachy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	img_temp = np.ones((400,400),np.uint8)#empty image to display the result

	for no in range(len(contours)):
		if cv2.contourArea(contours[no])<200:
			continue
		#centroid
		M = cv2.moments(contours[no])
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])
        position = find_position(cx,cy,rows,columns,3)

		#min area rectangle
        rect = cv2.minAreaRect(contours[no])
		box = cv2.cv.BoxPoints(rect)
		box = np.int0(box)

		#finding the ratio of areas
		area_ratio = cv2.contourArea(contours[no])/cv2.contourArea(box)

		#text for output image
		shape = 'none'
		if (area_ratio > 0.95):
			shape = 'rect'
		elif (area_ratio>0.65) & (area_ratio<0.95):
			shape = 'Cir'
		elif (area_ratio<0.65):
			shape = 'Tri'

		#draw on the new image
		#cv2.putText(img_temp[x],shape,(cx,cy),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1,(255,255,255),2)
		#cv2.drawContours(img_temp[x], contours,-1, (255,255,255), 2)
		#cv2.drawContours(img_temp,[box],0,(255,255,255),2)
		#cv2.imshow('img_temp'+str(x),img_temp[x])
		color_name = None
		if (x==0):
			color_name = 'red'
		elif(x==1):
			color_name = 'green'
		elif(x==2):
			color_name = 'blue'

		info={'point':(cx,cy),'pos':position,'shape':shape,'color':color_name,'con_area':cv2.contourArea(contours[no]),'min_area':cv2.contourArea(box)}
		details_objects.append(info)

for obj in details_objects:
    dest = obj['point']


	while(True):
		cv2.waitKey(250)
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

        if(distance <800):
            break
		
    



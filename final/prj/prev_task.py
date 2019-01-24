#arena: A-F(1-6),1-9

#position of the points in the arena: '1' based index
#shapes: stores the objects present in the location(index)-> 0:obstacle 1:circle 2:square 3:triangle
#colors: stores the color values->0:red 1:green 2:blue

import cv2
import numpy as np
import cv2.cv as cv
import math
import sys
import time

#import comm
import algo_mod
import angle_mod

##################################################################################################################
# FUNCTION DEFINITIONS
##################################################################################################################  

#rotates the bot
#input:angle,time delay
#output: rotates the robot
def rotate(ang,time_delay):
    if(ang<0):
        comm.send_data('<a');cv2.waitKey(100);
    else:
        comm.send_data('<k');cv2.waitKey(100);

    ang = abs(ang)

    if(ang > 99):
        d = ang/100
        n = ang - 100*d
        comm.send_data(str(d));cv2.waitKey(100);

        d = n/10
        n = n - 10*d
        comm.send_data(str(d));cv2.waitKey(100);
        comm.send_data(str(n));cv2.waitKey(100);

    else:
        d = ang/10
        n = ang - 10*d
        comm.send_data(str(d));cv2.waitKey(100);
        comm.send_data(str(n));cv2.waitKey(100);

    comm.send_data('>');cv2.waitKey(100);
    cv2.waitKey(time_delay)

 

#draw Triangles for the triangle detection algorithm
#input: three points of the triangle,source image
#output:draws a triangle
def drawTriangle(p1,p2,p3,img):
    cv2.line(img,p1,p2,(255,255,255),1)
    cv2.line(img,p2,p3,(255,255,255),1)
    cv2.line(img,p3,p1,(255,255,255),1)

#draw SQUARES for the square detection algorithm
#input: four points of the triangle,source image
#output:draws a triangle
def drawSquare(p1,p2,p3,p4,src_img):
    cv2.line(src_img,p1,p2,(255,255,255),1)
    cv2.line(src_img,p1,p3,(255,255,255),1)
    cv2.line(src_img,p1,p4,(255,255,255),1)
    
    cv2.line(src_img,p2,p3,(255,255,255),1)
    cv2.line(src_img,p2,p4,(255,255,255),1)
    
    cv2.line(src_img,p3,p4,(255,255,255),1)


def triangle_area(points):
    d1 = math.sqrt((points[0][0]-points[1][0])*(points[0][0]-points[1][0])+(points[0][1]-points[1][1])*(points[0][1]-points[1][1]))
    d2 = math.sqrt((points[1][0]-points[2][0])*(points[1][0]-points[2][0])+(points[1][1]-points[2][1])*(points[1][1]-points[2][1]))
    d3 = math.sqrt((points[2][0]-points[0][0])*(points[2][0]-points[0][0])+(points[2][1]-points[0][1])*(points[2][1]-points[0][1]))
    d = (d1+d2+d3)/3.0
    area = (math.sqrt(3)/4.0)*d*d
    return area

#finds to which block the coordinates belong to
#input: pixel coordinates,source image(single channel image)
#output: row and column number to which it belongs to
def findBlock(point,img):
    global row_margin
    x = point[0]
    y = point[1]
    row,col = img.shape
    img = img[row_margin:rows-row_margin,0:col]
    row,col = img.shape

    c = math.ceil(x/(col/9.0))
    r = math.ceil(y/(row/6.0))
    return (r,c)


#finds to which block the coordinates belong to
#input: pixel coordinates,source image(multi channel image)
#output: row and column number to which it belongs to
def findBlockColor(point,img):
    global row_margin
    x = point[0]
    y = point[1]
    row,col,_ = img.shape
    img = img[row_margin:row-row_margin,0:col]
    row,col,_ = img.shape

    c = math.ceil(x/(col/9.0))
    r = math.ceil(y/(row/6.0))
    return (r,c)

#returns the position on the arena
#input: pixel coordinates
#output: position on the arena
def getPositionFromCoord(point):
    r = point[0]
    c = point[1]
    return c+(r-1)*9

#return ROI of the desired position
#input:source image,position on the arena
#output: ROI(Region of Image) of the source image for required position
def getROI(img,pos):
    global row_margin
    #finds dimensions of arena
    rows,cols,_ = img.shape
    img = img[row_margin:rows-row_margin,0:cols]
    rows,cols,_ = img.shape

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
    temp_img =  img[rows_start:rows_end,cols_start:cols_end]
    return temp_img

#finds the row no and column no
#input:position on the arena
#output:row and column number(tuple)
def getCoord(pos):
    c = pos%9
    if(c == 0):
        c = 9
        r = pos/9
        return (r,c)
    r = (pos/9) +1
    return (r,c)

#finds the position of bot on the arena
#input: captured image(current),forward and backward threshold values(for inRange function)
#output: bot forward coordinate,bot centre coordinates,output of inRange function followed by morphological operation
def find_bot(capf,forward_values,backward_values):
    global row_margin
    rows,cols,_ = capf.shape
    capf = capf[row_margin:rows-row_margin,0:cols]
    rows,cols,_ = capf.shape


    blur_img = cv2.bilateralFilter(capf,5,50,50)
    blur_img = cv2.medianBlur(blur_img,5)
    capy = cv2.cvtColor(blur_img,cv2.COLOR_BGR2HSV)
    img_temp = np.ones(capy.shape,np.uint8)#empty image to display the result

    for dir in range(2):
        if(dir == 0):
            low_values = forward_values[0]
            high_values = forward_values[1]
        else:
            low_values = backward_values[0]
            high_values = backward_values[1]

           
        #color filtering
        mask = cv2.inRange(capy,low_values,high_values)
        #opening
        mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
        mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
        #closing
        mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
        mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
        #cv2.imshow('mask',mask)
        
        #finding contours of the thresholded image
        ctrs,hierachy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(img_temp, ctrs,-1, (255,255,255), 2)
        
        
        for no in range(len(ctrs)):
            if cv2.contourArea(ctrs[no])>2000:
                #centroid
                M = cv2.moments(ctrs[no])
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                
                if (dir == 0):
                    bot_f = (cx,cy)
                    #print 'for:'+str(bot_f)
                    break
                else:
                    #bot_c = ((cx+bot_f[0])/2,(bot_f[1]+cy)/2)
                    bot_c = (cx,cy)
                    #print 'cent:'+str(bot_c)
                    break
        cv2.putText(img_temp,str(dir),(cx,cy),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1,(255,255,255),2)
    #cv2.imshow("bot",img_temp)

    #cv2.waitKey(0)
    return bot_f,bot_c,img_temp






#return pixel x and pixel y centre for the position mentioned
#input:position on the arena,source image
#output:centre of the specific block(ROI) in accordance to the position on the arena

def getxy(pos,img):
    global row_margin
    #finds dimensions of arena
    rows,cols,_ = img.shape
    img = img[row_margin:rows-row_margin,0:cols]
    rows,cols,_ = img.shape

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

    x = (cols_start+cols_end)/2
    y = (rows_start+rows_end)/2
    return (x,y)

#moves the bot in the direction specified
#input:null
#output:null
def move_right():
    comm.send_data('6')
    cv2.waitKey(50)
    comm.send_data('5')
   
def move_left():
    comm.send_data('4')
    cv2.waitKey(50)
    comm.send_data('5')
   

def move_forward(time_delay):
    comm.send_data('8')
    cv2.waitKey(time_delay)
    comm.send_data('5')
   
def move_backward():
    comm.send_data('8')
    cv2.waitKey(50)
    comm.send_data('5')

    
#empty function used for trackbar
#input:null
#output:null
def nothing(x):
    pass





#################################################################################################################
# GLOBAL VARIABLES
#################################################################################################################

src_img = 0
shapes = []
sizes=[]
colors=[]
centroids = []
contour_areas = []
rows = 0
cols = 0
row_margin = 10

values=[]
#values = [(138,69,70),(180,255,237),(25,124,20),(102,255,126),(95,124,45),(136,255,174),(95,124,45),(136,255,174),(95,124,45),(136,255,174)]
#values = [(57,152,180),(180,204,251),(57,137,56),(180,255,105),(121,167,56),(180,255,255),(0,67,125),(99,255,255),(50,67,112),(180,158,255)]
#values = [(167,144,145),(180,201,192),(9,93,49),(97,255,160),(90,105,92),(162,255,180),(0,71,97),(157,255,255),(88,57,124),(180,255,255)] #morning1
#values = [(170,100,98),(180,255,255),(20,21,0),(103,255,107),(93,155,41),(118,255,255),(0,71,97),(157,255,255),(88,57,124),(180,255,255)] #night1
#values = [(170,44,88),(180,255,255),(18,38,5),(105,255,140),(95,93,29),(117,255,255),(0,71,97),(157,255,255),(88,57,124),(180,255,255)]#night2
values = [(168,0,43),(180,255,255),(60,85,13),(102,255,140),(90,25,65),(157,255,255),(0,71,97),(157,255,255),(88,57,124),(180,255,255)]#night3


matches = []



##################################################################################################################
# MAIN CODE STARTS HERE
##################################################################################################################    

 

#initialisation for camera
cap = cv2.VideoCapture(1)

cv2.waitKey(0)

while(1):
    _,src_img = cap.read()
    cv2.imshow('live',src_img)
    _,img_src = cap.read()
    _,img_src2 = cap.read()
    if(cv2.waitKey(100) & 0xFF == ord('q')):
        cv2.waitKey(200)
        cv2.destroyAllWindows()
        break

#initialising the global variables rows and cols and cropping the unnecessary portion of arena
rows,cols,_ = src_img.shape
src_img = src_img[row_margin:rows-row_margin,0:cols]
img_src = img_src[row_margin:rows-row_margin,0:cols]
src_img = src_img[row_margin:rows-row_margin,0:cols]

rows,cols,_ = src_img.shape


#stores from 0 to 54 but we use 1 to 54 w.r.t position
for x in range(55):
    shapes.append(-1)
    sizes.append(-1)
    colors.append(-1)
    centroids.append(-1)
    contour_areas.append(-1)

'''

# create trackbars for color change
cv2.namedWindow('pallete',cv2.WINDOW_AUTOSIZE)
cv2.createTrackbar('low_h','pallete',0,180,nothing)
cv2.createTrackbar('low_s','pallete',0,255,nothing)
cv2.createTrackbar('low_v','pallete',0,255,nothing)
cv2.createTrackbar('high_h','pallete',180,180,nothing)
cv2.createTrackbar('high_s','pallete',255,255,nothing)
cv2.createTrackbar('high_v','pallete',255,255,nothing)
cv2.createTrackbar('blur','pallete',5,10,nothing)


for alpha in range(5):
    #loop for trackbar
    while(1):
        rows,columns,_ = src_img.shape
        blur_quant = 5
        #blur_img = cv2.GaussianBlur(src_img,(5,5),0)
        blur_img = cv2.bilateralFilter(src_img,blur_quant,50,50)
        blur_img = cv2.medianBlur(blur_img,5)
        img = cv2.cvtColor(blur_img,cv2.COLOR_BGR2HSV)
    
        if cv2.waitKey(1) & 0xFF == ord('q'):
            values.append(lower_values)
            values.append(higher_values)
            print str(lower_values)+' , '+str(higher_values)
            break

        # get current positions of four trackbars
        blur_quant = cv2.getTrackbarPos('blur','pallete')

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
 '''
cv2.destroyAllWindows()


# DETECTING CIRCLES
img = cv2.cvtColor(src_img,cv2.COLOR_BGR2GRAY)
img = cv2.bilateralFilter(img,7,50,50)
img = cv2.medianBlur(img,5)
circles = cv2.HoughCircles(img,cv.CV_HOUGH_GRADIENT,1,20,param1=60,param2=25,minRadius=2,maxRadius=25)

circles = np.uint16(np.around(circles))
for i in circles[0,:]:
    t =  findBlock((i[0],i[1]),img)
    shapes[int(getPositionFromCoord(t))] = 1 

    #saving centroids
    centroids[int(getPositionFromCoord(t))] = (i[0],i[1])
    #saving area of the object
    contour_areas[int(getPositionFromCoord(t))] = np.pi * i[2] * i[2]
    print str(int(getPositionFromCoord(t))) + ' :circles'

    # draw the outer circle
    cv2.circle(img,(i[0],i[1]),i[2],(255,255,255),2)
    cv2.putText(img,'circle',(i[0],i[1]),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1,(255,255,255),2)
cv2.imshow('circles_detect',img)
cv2.waitKey(0)
cv2.destroyAllWindows()



        
blur_img = cv2.bilateralFilter(img_src,5,50,50)
blur_img = cv2.medianBlur(blur_img,5)
img = cv2.cvtColor(blur_img,cv2.COLOR_BGR2HSV)


#SQUARE DETECTION
for pos in range(1,55):
    points = []
    box = 0
    temp_img = getROI(img_src2,pos)

    #finding corner points
    gray = cv2.cvtColor(temp_img,cv2.COLOR_BGR2GRAY)
    corners = cv2.goodFeaturesToTrack(gray,4,0.01,10)
    if(corners == None):
        continue
    #print 'in pos: '+str(pos)
    corners = np.int0(corners)
    for i in corners:
        x,y = i.ravel()
        points.append((x,y))
        cv2.circle(temp_img,(x,y),3,255,-1)


    #finding contour area
    blank_img = np.zeros((100,100,3), np.uint8)
    
    try:
        drawSquare(points[0],points[1],points[2],points[3],blank_img)
    except IndexError:
        continue

    blank_img = cv2.cvtColor(blank_img,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(blank_img,(0,0,10),(180,255,255))

    contours,hierachy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    lcontour = contours[0]
    for no in range(len(contours)):
        if cv2.contourArea(contours[no])<20:
            continue
        if cv2.contourArea(contours[no])>cv2.contourArea(lcontour):
            lcontour = contours[no]

    #min area rectangle
    rect = cv2.minAreaRect(lcontour)
    box = cv2.cv.BoxPoints(rect)
    box = np.int0(box)

    #finding the ratio of areas
    try:
        area_ratio = cv2.contourArea(lcontour)/cv2.contourArea(box)
    except ZeroDivisionError:
        continue
        
        
    #print 'area_ratio' + str(area_ratio)
    #print 'contour area: ' +str(cv2.contourArea(box))

    cx = (points[0][0]+points[1][0]+points[2][0]+points[3][0])/4
    cy = (points[0][1]+points[1][1]+points[2][1]+points[3][1])/4
        
  
    if( area_ratio >0.75 and cv2.contourArea(box)<400 and shapes[pos]!= 1):
        print str(pos) + ' :square'

        shapes[pos] = 2
        centroids[pos] = (cx,cy)
        contour_areas[pos] = cv2.contourArea(box)

    elif(area_ratio > 0.75 and cv2.contourArea(box) > 1000 and cv2.contourArea(box)<2800 and shapes[pos]!= 1):
        print str(pos) + ' :OBSTACLE'

        shapes[pos] = 0
        centroids[pos] = (cx,cy)
        contour_areas[pos] = cv2.contourArea(box)
    else:
        #print 'false'
        pass

    #cv2.imshow('frame',temp_img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()



# FINDING TRIANGLES
#remember to remove the circles from triangle - IMPORTANT


for pos in range(1,55):
    points = []                        #stores the points of the triangle as a list
    box = 0
    temp_img = getROI(src_img,pos)     #ROI of every block of the arena
    tri_area = 0

    #print 'in pos: '+str(pos)

    #finding corner points
    gray = cv2.cvtColor(temp_img,cv2.COLOR_BGR2GRAY)
    corners = cv2.goodFeaturesToTrack(gray,3,0.01,10)
    if(corners == None):
        continue
    corners = np.int0(corners)
    for i in corners:
        x,y = i.ravel()
        points.append((x,y))
        #cv2.circle(temp_img,(x,y),3,255,-1)

    min_angle = 40
    max_angle = 80

    try:
        equi_angle = False
        angle1 =    abs(angle_mod.angle_between(points[0],points[2],points[1]))
        angle2 =    abs(angle_mod.angle_between(points[1],points[0],points[2]))
        angle3 =    abs(angle_mod.angle_between(points[2],points[1],points[0]))

        if( angle1< max_angle and angle2<max_angle and angle3<max_angle):
            if(angle1>min_angle and angle2>min_angle and angle3>min_angle):
                equi_angle = True

    except TypeError:
        continue
    except IndexError:
        continue

    try:
        tri_area = triangle_area(points)
    except TypeError:
        continue
    except IndexError:
        continue

    #cv2.contourArea(box)<400
    if(equi_angle and tri_area<400 and shapes[pos]!= 1 and shapes[pos]!= 3):
        shapes[pos] = 3
        cx = (points[0][0]+points[1][0]+points[2][0])/3
        cy = (points[0][1]+points[1][1]+points[2][1])/3
        centroids[pos] = (cx,cy)
        contour_areas[pos] = tri_area

        print str(pos) + ' :tri'
    else:
        pass




# COLOR detection
for x in range(3):

    cv2.waitKey(0)
    print values[2*x]
    print values[(2*x)+1]
    #color filtering
    mask = cv2.inRange(img,values[2*x],values[(2*x)+1])
    #opening
    mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
    mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)
    #closing
    mask = cv2.erode(mask,np.ones((5,5),np.uint8),iterations = 1)
    mask = cv2.dilate(mask,np.ones((5,5),np.uint8),iterations = 1)


    #finding contours of the thresholded image
    contours,hierachy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    img_temp = np.ones((480,640),np.uint8)#empty image to display the result

    for no in range(len(contours)):
        #print cv2.contourArea(contours[no])
        if cv2.contourArea(contours[no])<50:
            continue

        cnt = contours[no]
        epsilon = 0.1*cv2.arcLength(cnt,True)
        approx = cv2.approxPolyDP(cnt,epsilon,True)
        cv2.drawContours(img_temp, approx, -1, (255,255,255), 1)
        

        #centroid
        M = cv2.moments(contours[no])
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        position = getPositionFromCoord(findBlockColor((cx,cy),src_img))
        position = int(position)
        cv2.putText(img_temp,str(no),(cx,cy),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1,(255,255,255),2)


        #min area rectangle
        rect = cv2.minAreaRect(approx)
        box = cv2.cv.BoxPoints(rect)
        box = np.int0(box)

        try:
            #finding the ratio of areas
            area_ratio = cv2.contourArea(approx)/cv2.contourArea(box)
        except ZeroDivisionError:
            continue
        try:
            if( shapes[position] != -1):
                colors[position] = x
                #centroids[position] = (cx,cy)
                #contour_areas[position] = cv2.contourArea(approx) 
        except:
            print 'error at: '+str(position)
            '''
        else:
            #text for output image
            if (area_ratio > 0.85):
                shapes[position] = 2
                colors[position] = x
                centroids[position] = (cx,cy)
                contour_areas[position] = cv2.contourArea(approx) 

            elif (area_ratio>0.65) & (area_ratio<0.85):
                shapes[position] = 1
                colors[position] = x
                centroids[position] = (cx,cy)
                contour_areas[position] = cv2.contourArea(approx) 

            elif (area_ratio<0.65):
                shapes[position] = 3
                colors[position] = x
                centroids[position] = (cx,cy)
                contour_areas[position] = cv2.contourArea(approx)
        '''

    cv2.imshow('contours'+str(x),img_temp)
    
#########################################################################

arr_objects = []

#displaying the detected objects
print '\nDETECTED OBJECTS'
for x in range(len(shapes)):
    if(shapes[x] != -1):
        arr_objects.append(x)
        print str(x)+' : '+str(shapes[x])+' ,\tcolor: '+str(colors[x])+' ,\tarea: '+str(contour_areas[x])

#sending to algo_module(step1 of algo_mod)
algo_mod.set_objects_positions(arr_objects)

#matching the results
print '\nMATCHES'
for x in (1,10,19,28,37,46):#make the values -1
    for y in range(1,55):
        ctr = getxy(y,src_img)
        cv2.putText(src_img,str(y),(ctr[0],ctr[1]+row_margin),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,0.5,(255,255,255),2)
        if( x != y and shapes[x] != -1 and colors[x]!=-1 and shapes[x] == shapes[y] and colors[x] == colors[y]):
            if(y%9 != 1 and abs(contour_areas[y] - contour_areas[x]) < 60):
                #saving the matched object as a source,destination pair
                matches.append((y,x))
                #cv2.line(src_img,centroids[y],centroids[x],(255,255,255),3)
                cv2.line(src_img,getxy(y,src_img),getxy(x,src_img),(255,255,255),3)
                
                # to make only one match with the door area object
                #shapes[x] = shapes[y] = -1
                print str((y,x))


#shows the matches found and waits for the user to continue the program
cv2.imshow('match',src_img)
print 'DO YOU WANT TO CONTINUE'
if(cv2.waitKey(0) & 0xFF == ord('n')):
    cv2.destroyAllWindows()
    sys.exit()


############################################################################
#MOVEMENT OF BOT
###########################################################################

forward_values = (values[6],values[7])
backward_values = (values[8],values[9])
#threshold values for far region to the destination
thresh_ang = 25
thresh_dis = 2000
#threshold values for near region to the destination
thresh_ang_inn = 15
thresh_dis_inn = 1500

#for obj in matches:
while(True):
    capz = 0
    j=15
    while(j>0):
        _,capz = cap.read()
        cv2.waitKey(10)
        j = j-1
        cv2.imshow('botc',capz)
    
    bf,bc,img_temp = find_bot(capz,forward_values,backward_values)
    route_planned = algo_mod.find_route(17,38,1,1)
    print route_planned
    for pt in route_planned:
        dest = getxy(pt,capz)
        while(True):
            capz = 0
            j=15
            while(j>0):
                _,capz = cap.read()
                cv2.waitKey(10)
                j = j-1
            cv2.imshow('botc',capz)

            bf,bc,img_temp = find_bot(capz,forward_values,backward_values)
            cv2.line(img_temp,bc,dest,(255,255,255),1)
            cv2.imshow('bot',img_temp)

            angle = angle_mod.angle_between(bf,dest,bc)
            angle = int(angle)
            distance = (dest[0]-bc[0])*(dest[0]-bc[0]) + (dest[1]-bc[1])*(dest[1]-bc[1])
            print str(angle) +" , "+ str(distance)

            if(abs(angle) > thresh_ang and distance > thresh_dis_inn):
                print 'rotate: '+str(angle)
                t_delay = abs(angle * (3000/360))
                rotate(angle,t_delay)

            elif(distance < thresh_dis):
                if(distance < thresh_dis_inn):
                    break
                elif(abs(angle) > thresh_ang_inn):
                    print '\t\t\t\tSLOW ROTATE'+str(angle)
                    t_delay = abs(angle * (3000/360))
                    rotate(angle,t_delay)
                elif(distance > thresh_dis_inn):
                    move_forward(150)
                    
            
            elif(distance > thresh_dis):
                print '\t\t\t\tFORWARD LARGE'
                #k = 60
                k = 40
                t = distance/k
                move_forward(t)
        cv2.waitKey(3000)

cv2.destroyAllWindows()
cap.release()

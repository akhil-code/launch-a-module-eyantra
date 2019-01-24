#make the graph for the dimensions of (9x6)
import cv2
import numpy as np
import time


graph = []                  #'1' based index but its constituents are absolute
parent = []
objects_position = []
V = 54     #No of vertices in the grid
details_source = []


'''
*Function Name: find_position
*Input: x coordinate,y coordinate,number of rows,no of columns,number of rows or columns
*Output: position number in the grid
*Logic: Finds out in which grid point it belongs to(out of 1 to 100)
*Example Call:find_position(3,4,10,10,10)
'''
#edited
def find_position(x,y,r,c,no_rows,no_cols):
    x_pos = None
    y_pos = None
    pos = None
    
    for i in range(no_cols):
        if x>(c/no_cols)*i and x<(i+1)*(c/no_cols):
            x_pos = i
            break
    
    for i in range(no_rows):
        if y>(r/no_rows)*i and y<(i+1)*(r/no_rows):
            y_pos = i
            break
    
    pos = x_pos + 1 + no_cols*y_pos
    return pos


'''
*Function Name: find_details
*Input: position
*Output: (color,shape) of the object in that position
*Logic: matches the position with all the positions available in the variable details_source
*Example Call: find_details(44)
'''
#edited
def find_details(pos):
    for x in details_source:
        if x['position'] == pos:
            color = x['color']
            shape = x['shape']
            return (color,shape)

        
'''
*Function Name: compare
*Input: two points p1 and p2
*Output: route betweent the two points
*Logic: it uses dijkistra's algorithm to find the shortest route between two points
*Example Call: compare(11,22)
'''
#edited
def compare(p1,p2):
    global graph,parent

    #for adjacent objects
    if(find_details(p1) == find_details(p2) and (abs(p1-p2) == 9 or abs(p1-p2) == 1)):
        return[p2,p1]

    #inserting the points
    insert_point(p1)
    insert_point(p2)

    #reset parent list
    for x in range(55):
        parent[x] = -1

    dijkistra(graph,p1)
    
    #deleting the points after algo
    delete_point(p1)
    delete_point(p2)
    return ext_route(p2)


'''
*Function Name: delete_point
*Input: position
*Output: NULL
*Logic: it deletes the required point from the grid
*Example Call: delete_point(33)
'''
#edited
#eliminates the point from the grid(use it to remove obstacle)
def delete_point(pos):
    #delete the element(empty the point elements-but donot delete it)
    #find it's adjacent points and eliminate the point from it
    global graph
    #print "should delete"+str(pos)
    #print "values at "+str(pos)+" : "+str(graph[pos-1])
    for x in graph[pos]:
        #print "-> "+str(graph[x-1])
        graph[x].remove(pos)
    graph[pos] = []

'''
*Function Name:insert_point
*Input: position
*Output: NULL
*Logic: it adds the point to the grid
*Example:insert_point(4)
'''

def insert_point(x):
    global objects_position
    temp = []
    if(x%9 != 1):                          #left sided objects
        try:
            objects_position.index(x-1)
        except ValueError:
            temp.append(x-1)
            graph[x-1].append(x)
        else:
            pass
    if(x%9 != 0):                          #right sided objects
        try:
            objects_position.index(x+1)
        except ValueError:
            temp.append(x+1)
            graph[x+1].append(x)
        else:
            pass
    if(x-9 >0 and x-9<55):               #for objects in between
        try:
            objects_position.index(x-9)
        except ValueError:
            temp.append(x-9)
            graph[x-9].append(x)
        else:
            pass
    if(x+9 >0 and x+9<55):
        try:
            objects_position.index(x+9)
        except ValueError:
            temp.append(x+9)
            graph[x+9].append(x)
        else:
            pass
    graph[x] = temp
    #print 'inserted at '+str(x)+" "+ str(temp)


'''
*Function Name: ext_route
*Input: point
*Output: return the route
*Logic: it finds the parent node or point from the parent array
*Example: ext_route(55)
'''
#edited
#routes the distance in backward direction
def ext_route(ptr):
    global parent
    route = []
    reroute = []
    route.append(ptr)
    
    while(parent[ptr]>0):
        route.append(parent[ptr][0])
        ptr = parent[ptr][0]
    for x in range(1,len(route)+1):
        reroute.append(route[-x])
    return reroute


'''
*Function Name: position_xy
*Input: position on grid
*Output: return the (x,y) coordinate of the position given as input
*Logic: calculate the x,y coordinate according to the given point
*Example: position_xy(48)
'''
#find the coordinates if provided with the position
#edited
def position_xy(p):
    if(p%9 == 0):
        y = p/9
    else:
        y = (p/9)+1
    
    if(p%9 != 0):
        x = p%9
    else:
        x = 9
    return (x,y)

'''
*Function Name: manhattan
*Input: points p1 and p2
*Output: return the manhattan distance between the two points
*Logic: manhattan distance is the sum of distance taken along the x axis and y axis in the coordinate plane
*Example: manhattan((1,6),(2,8))
'''
#edited
#finds the manhattan distance
def manhattan(p1,p2):
    xdiff = abs(position(p1)[0]-position(p2)[0])
    ydiff = abs(position(p1)[1]-position(p2)[1])
    return (xdiff,ydiff)

'''
*Function Name:graph_dist
*Input: graph,point p1,point p2
*Output: returns 1 if there is a link
*Logic: returns 1 if there is a link between the two points given as input
*Example:graph_dist(graph,5,6)
'''
#graph[u][v] == distance between vertices u and v
def graph_dist(graph,p1,p2):
    for x in graph[p1]:
        if x == p2:
            return 1
    '''
    for x in range(len(graph[p1-1])):
        output = 0
        if(graph[p1-1][x] == p2):
            return 1
    #return output
    '''

'''
*Function Name:minDistance
*Input: two arrays named dist(distance array) and sptSet(shortest path set)
*Output: the minimum distance using the distance array and shorest path set
*Logic: It is a utility function of the dijkistra's algorithm
*Example:minDistance(dist,sptSet)
'''

#finds the minimum distance(code part of dijkistra's algo)
def minDistance(dist,sptSet):
    min = 999
    global V
    for v in range(V+1):
        if (sptSet[v] == 0 and dist[v] <= min):
            min = dist[v]
            min_index = v
    return min_index


'''
*Function Name:dijkistra
*Input:graph and source point
*Output:Applies the dijkistra algorithm to find the shortest distances
*Logic: It is a graph algorithm used to calculate the least distance to all other points in the grid
*Example: dijkistr(graph,45)
'''

#main dijkistra's function
def dijkistra(graph,src):
    global V
    dist = []
    sptSet = []

    for i in range(V+1):
        dist.append(999)
        sptSet.append(0)

    dist[src] = 0
    for count in range(1,V):
        u = minDistance(dist,sptSet)
        sptSet[u] = 1
        for v in range(1,V+1):
            if((not sptSet[v]) and graph_dist(graph,u,v) and dist[u] != 999 and dist[u]+graph_dist(graph,u,v) < dist[v]):
               dist[v] = dist[u]+graph_dist(graph,u,v)
               parent[v] = [u]



#initialisation
#src_img: used to store the image
src_img = cv2.imread('test_image4.jpg',cv2.IMREAD_COLOR)
#rows,columns,_: used to store the dimensions of the image
rows,columns,_ = src_img.shape #finding the dimensions
#blur_img: used to save the blurred image
blur_img = cv2.GaussianBlur(src_img,(5,5),0)#blur
#img: used to save the final image used for further processing
img = cv2.cvtColor(blur_img,cv2.COLOR_BGR2HSV)#cvtcolor
cv2.imshow('input',src_img)

#used to save the mask items
mask=[0,0,0,0]
#used to save the temp
img_temp=[0,0,0,0]
#values are in order of red,green,blue,yellow
#values: used to store the color ranges
values=((0,211,0),(15,255,255),(42,134,0),(79,255,255),(68,124,23),(143,255,255),(0,0,0),(180,255,3))

#applying four times in order to apply transformation on red, blue, green and black objects
for x in range(4):

    #color filtering
    mask[x] = cv2.inRange(img,values[2*x],values[(2*x)+1])
    #opening
    mask[x] = cv2.erode(mask[x],np.ones((5,5),np.uint8),iterations = 1)
    mask[x] = cv2.dilate(mask[x],np.ones((5,5),np.uint8),iterations = 1)
    #closing
    mask[x] = cv2.erode(mask[x],np.ones((5,5),np.uint8),iterations = 1)
    mask[x] = cv2.dilate(mask[x],np.ones((5,5),np.uint8),iterations = 1)

for x in range(4):#red,green,blue,black(obstacle)
    #finding contours of the thresholded image
    contours,hierachy = cv2.findContours(mask[x],cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    img_temp[x] = np.ones((400,400),np.uint8)#empty image to display the result

    for no in range(len(contours)):
        if cv2.contourArea(contours[no])<200:
            continue
        #centroid
        M = cv2.moments(contours[no])
        #cx,cy: x and y coordinates of the centroid
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        position = find_position(cx,cy,rows,columns,no_rows=6,no_cols=9)
    
        #min area rectangle
        rect = cv2.minAreaRect(contours[no])
        box = cv2.cv.BoxPoints(rect)
        box = np.int0(box)
    
        #finding the ratio of areas
        area_ratio = cv2.contourArea(contours[no])/cv2.contourArea(box)

        #text for output image
        shape = 'none'
        if (area_ratio > 0.95):
            shape = '4-sided'
        elif (area_ratio>0.65) & (area_ratio<0.95):
            shape = 'Circle'
        elif (area_ratio<0.65):
            shape = 'Triangle'

        #draw on the new image
        cv2.putText(img_temp[x],shape,(cx,cy),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1,(255,255,255),2)
        cv2.drawContours(img_temp[x], contours,-1, (255,255,255), 2)
       
        color_name = None
        if (x==0):
            color_name = 'red'
        elif(x==1):
            color_name = 'green'
        elif(x==2):
            color_name = 'blue'
        elif(x==3):
            color_name = 'black'
        #adds details regarding the objects in the image based on the processing done above
        info={'position':position,'shape':shape,'color':color_name,'contour_area':cv2.contourArea(contours[no]),'min_area':cv2.contourArea(box)}
        details_source.append(info)

#first sorting the given image
for i in range(len(details_source)-1):
    for j in range(i,len(details_source)):
        if(details_source[i]['position']>details_source[j]['position']):
            t = details_source[i]
            details_source[i] = details_source[j]
            details_source[j] = t
#print '\nafter sorting SOURCE'

'''
#code for printing the output of all the objects in the image
for x in range(len(details_source)):
    print details_source[x]
'''
#code for making the output1
output1=[]
for x in details_source:
    objects_position.append(x['position'])


for x in details_source:
    alpha = int(x['position'])
    output1.append(position_xy(alpha))



#code for converting grid to graph(initialisation)
#defining boundaries for the grid
#edited
graph.append(-1)
for x in range(1,55):
    temp = []
    if(x%9 != 1):          #left condition
        temp.append(x-1)
    if(x%9 != 0):          #right condition
        temp.append(x+1)
    if(x-9 >0 and x-9<55):
        temp.append(x-9)
    if(x+9 >0 and x+9<55):
        temp.append(x+9)
    
    graph.append(temp)


for x in range(55):
    parent.append(-1)

'''
#code for printing graph
for x in range(len(graph)):
    print str(x)+" : "+str(graph[x])
 '''

'''
#code for printing the parent matrix
print "\n the parent matrix is"
for x in range(len(parent)):
    print str(x)+"'s  ->  "+str(parent[x])

'''

#code for deleting all the obstacles from the grid
for x in range(len(details_source)):
    #if(details_source[x]['color'] == 'black'):
    delete_point(details_source[x]['position'])

print compare(27,46)
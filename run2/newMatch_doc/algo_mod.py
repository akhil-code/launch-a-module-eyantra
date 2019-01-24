'''
*Team id:eYRC-LM#448
*Author List: Akhil Guttula, Sai Kiran, Sai Gopal, Mohan
*Filename: algo_mod
*Theme: Launch a Module
*Functions:find_route,delete_point,insert_point,ext_route,graph_dist,minDistance,set_objects_positions,get_objects_positions,set_free_loc,get_neighbours,dijkistra
*Global Variables: graph,parent,objects_position,V
'''

import cv2
import numpy as np
import time
import sys


'''
*Function Name: find_route
*Input: position-1(source),position-2(destination),comparision details for source and destination
*Output: route between the source and destination using dijkistra algorithm
*Logic: uses dijkistra's algorithm to find the shortest path
*Example Call: find_route(9,46,1,1)
'''
#finds the route between the source and destination using dijkistra algorithm
def find_route(p1,p2,details_src,details_dest):
    global graph,parent,parentx,pathx_list

    #for adjacent objects
    if(details_src == details_dest and (abs(p1-p2) == 9 or abs(p1-p2) == 1)):
        if(p1%9 != 0 and p2 %9 != 0):
            return[p1,p2]

    #inserting the points
    insert_point(p1)
    insert_point(p2)

    

    #reset parent list
    for x in range(55):
        parent[x] = -1
        parentx[x] = []
    pathx_list = []

    dijkistra(graph,p1)

    
    #deleting the points after algo
    delete_point(p1)
    delete_point(p2)

    #finding the route that has minimum number of turns
    #short_len: has the shortest distance length obtained from dijkistra's algorithm
    short_len = len(ext_route(p2))
    #obtains all the paths using shortest path - dijkistra's algorithm
    printAllPaths(p2,p1,short_len)
    #selecting the path which has minimum number of turns
    min_pts = len(pathx_list[0])
    route = pathx_list[0]
    for obj in pathx_list:
        temp_pts = find_critical_pts(obj)
        if(len(temp_pts) < min_pts):
            route = obj
    route =  list(route)
    route.reverse()
    
    return route

'''
*Function Name: delete_point
*Input: position
*Output:removes the point from the grid(considers the point as an obstacle)
*Logic: deletes the point and also removes its existance from adjacent graph points
*Example Call:delete_point(22)
'''
#eliminates the point from the grid(use it to remove obstacle)
def delete_point(pos):
    #find it's adjacent points and eliminate the point from it
    global graph
    for x in graph[pos]:
        graph[x].remove(pos)
    graph[pos] = []

'''
*Function Name:insert_point 
*Input: position
*Output:inserts the point in the graph
*Logic:inserts the point in the graph and also includes as the neighbours in the adjacent graph points
*Example Call:insert_point(32)
'''

#inserts the point
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


'''
*Function Name: ext_route
*Input: destination point
*Output: a route depicting from which node the destination is reach
*Logic: uses parent array to find the parent node(node that is traversed before the destination node)
*Example Call:ext_route(11)
'''
#routes the path from source to destination
def ext_route(ptr):
    global parent
    route = []
    reroute = []
    route.append(ptr)
    
    while(parent[ptr]>0):
        route.append(parent[ptr][0])
        ptr = parent[ptr][0]
    route.reverse()
    return route



'''
*Function Name: graph_dist
*Input: graph,position-1,position-2
*Output:returns 1 as distance between two positions if there exists a link between the two positions
*Logic: checks if the the other position exists as neighbour point in the graph
*Example Call:graph_dis(graph,23,24)
'''
#graph[u][v] == distance between vertices u and v
def graph_dist(graph,p1,p2):
    for x in graph[p1]:
        if x == p2:
            return 1


'''
*Function Name: minDistance
*Input: arrays named dist(distance),sptSet(shortest path set)
*Output:
*Logic:
*Example Call:
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
*Function Name: set_objects_positions
*Input: an array of positions where the objects or obstacles are present
*Output: None
*Logic: sets the locations where there are objects or obstacles so that bot cannot traverse through it
*Example Call:set_objects_positions([11,16,23,34,48])
'''
#includes both objects and obstacles
def set_objects_positions(arr):
    global objects_position
    for x in arr:
        objects_position.append(x)
        delete_point(x)

'''
*Function Name: get_objects_positions
*Input: NULL
*Output: array of positions where the objects or obstacles are present
*Logic: return global array objects_position which stores the positions where the objects or obstacles are present
*Example Call:get_objects_positions()
'''
def get_objects_positions():
    global objects_position
    arr = objects_position
    return arr

'''
*Function Name: set_free_loc
*Input: source position
*Output:sets the location free i.e includes the point in the graph so that bot can traverse through it
*Logic: It is used when the specified position is made empty i.e after picking up the object from the point
*Example Call:set_free_loc(23)
'''
def set_free_loc(pos):
    global graph
    try:
        ind = objects_position.index(pos)
        del(objects_position[ind])
    except ValueError:
        pass
    insert_point(pos)

'''
*Function Name: get_neighbours
*Input: source position
*Output:returns the neighbouring positions of the source positions
*Logic: return the neighbouring positions of the current position
*Example Call:get_neighbours(34)
'''
#returns the neighbouring points to the current block
def get_neighbours(pos):
    global graph
    return graph[pos]



'''
*Function Name: dijkistra
*Input: graph,source position
*Output: finds the shortest distance from the source position to all other positions
*Logic: standard dijkistra's graph algorithm
*Example Call:dijkistra(graph,2)
'''
#main dijkistra's function
def dijkistra(graph,src):
    global V,parent,parentx
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
            if((not sptSet[v]) and graph_dist(graph,u,v) and dist[u] != 999 and dist[u]+graph_dist(graph,u,v) <= dist[v]):
               dist[v] = dist[u]+graph_dist(graph,u,v)
               parent[v] = [u]
               parentx[v].append(u)

def printAllPathsUtil(ux, dx, visitedx, pathx,short_len):
    global parentx,pathx_list
    # Mark the current node as visited and store in path
    visitedx[ux]= 1
    pathx.append(ux)
 
    # If current vertex is same as destination, then print
    # current path[]
    #print pathx
    if ux == dx and len(pathx) == short_len:
        pathx_list.append(tuple(pathx))

    else:
        # If current vertex is not destination
        #Recur for all the vertices adjacent to this vertex
        for i in parentx[ux]:
            if visitedx[i]== -1:
                printAllPathsUtil(i, dx, visitedx, pathx,short_len)
                     
    # Remove current vertex from path[] and mark it as unvisited
    pathx.pop()
    visitedx[ux]= -1
  
  
# Prints all paths from 's' to 'd'
def printAllPaths(sx, dx,short_len):
    global pathx_list
    # Mark all the vertices as not visited
    visitedx = []
    for x in range(55):
        visitedx.append(-1)
 
    # Create an array to store paths
    pathx = []
 
    # Call the recursive helper function to print all paths
    printAllPathsUtil(sx, dx,visitedx, pathx,short_len)

def find_critical_pts(route):
    target_pts = []
    diff = 99999
    temp_diff = 99999
    target_pts.append(route[0])
    for i in range(1,len(route)):
        temp_diff = route[i] - route[i-1]
        if(diff != 99999):
            if(diff != temp_diff):
                target_pts.append(route[i-1])
                diff = temp_diff
        diff = temp_diff
    target_pts.append(route[-1])
    return target_pts

###########################################################################################################
#GLOBAL VARIABLES
###########################################################################################################
#graph: stores the graph(grid) of the arena along with its neighbouring positions
graph = []                  #'1' based index but its constituents are absolute
#parent: used to store the parent node from which the current node has been travered
parent = []
parentx = []
pathx_list = []
#objects_position: used to store the positions at which objects are present
objects_position = []
#V: No of vertices in the graph(grid)
V = 54

 
###########################################################################################################


#defining boundaries for the grid
graph.append(-1)
for x in range(1,55):
    temp = []
    if(x%9 != 1):          #left boundary condition
        temp.append(x-1)
    if(x%9 != 0):          #right boundary condition
        temp.append(x+1)
    if(x-9 >0 and x-9<55): #upper boundary condition
        temp.append(x-9)
    if(x+9 >0 and x+9<55): #right boundary condition
        temp.append(x+9)
    
    graph.append(temp)

#initialising parent array
for x in range(55):
    parent.append(-1)
    parentx.append([])


#using algo module
#step1: call set_objects_positoins(arr[])
#step2: call find_route(source,destination,details_src(color,shape),details_dest(color,shape))
#step3:call insert to add that point of the arena i.e free space




    





import cv2
import numpy as np
import time

def find_route(p1,p2,details_src,details_dest):
    global graph,parent

    #for adjacent objects
    if(details_src == destails_dest and (abs(p1-p2) == 9 or abs(p1-p2) == 1)):
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

#edited
#eliminates the point from the grid(use it to remove obstacle)
def delete_point(pos):
    #find it's adjacent points and eliminate the point from it
    global graph
    for x in graph[pos]:
        graph[x].remove(pos)
    graph[pos] = []


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

#graph[u][v] == distance between vertices u and v
def graph_dist(graph,p1,p2):
    for x in graph[p1]:
        if x == p2:
            return 1


#finds the minimum distance(code part of dijkistra's algo)
def minDistance(dist,sptSet):
    min = 999
    global V
    for v in range(V+1):
        if (sptSet[v] == 0 and dist[v] <= min):
            min = dist[v]
            min_index = v
    return min_index

#includes both objects and obstacles
def set_objects_positions(arr):
    global objects_position
    for x in arr:
        objects_position.append(x)
        delete_point(x)

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

###########################################################################################################
#GLOBAL VARIABLES
###########################################################################################################
graph = []                  #'1' based index but its constituents are absolute
parent = []
objects_position = []
V = 54     #No of vertices in the grid
###########################################################################################################




#defining boundaries for the grid
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

#initialising parent array
for x in range(55):
    parent.append(-1)


#using algo module
#step1: call set_objects_positoins(arr[])
#step2: call find_route(source,destination,details_src(color,shape),details_dest(color,shape))
#step3:call insert to add that point of the arena i.e free space

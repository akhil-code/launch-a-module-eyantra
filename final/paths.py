def printAllPathsUtil(ux, dx, visitedx, pathx):
    global parentx
    # Mark the current node as visited and store in path
    visitedx[ux]= 1
    pathx.append(ux)
 
    # If current vertex is same as destination, then print
    # current path[]
    #print pathx
    if ux == dx:
        print pathx
    else:
        # If current vertex is not destination
        #Recur for all the vertices adjacent to this vertex
        for i in parentx[ux]:
            if visitedx[i]== -1:
                printAllPathsUtil(i, dx, visitedx, pathx)
                     
    # Remove current vertex from path[] and mark it as unvisited
    pathx.pop()
    visitedx[ux]= -1
  
  
# Prints all paths from 's' to 'd'
def printAllPaths(sx, dx):
 
    # Mark all the vertices as not visited
    visitedx = []
    for x in range(55):
        visitedx.append(-1)
 
    # Create an array to store paths
    pathx = []
 
    # Call the recursive helper function to print all paths
    printAllPathsUtil(sx, dx,visitedx, pathx)
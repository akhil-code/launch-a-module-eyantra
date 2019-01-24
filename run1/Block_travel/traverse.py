import algo_mod
import sys

def find_critical_pts_mod(route):
    count = 0
    target_pts = []
    diff = 99999
    temp_diff = 99999
    target_pts.append(route[0])
    for i in range(1,len(route)):
        temp_diff = route[i] - route[i-1]
        if(diff != 99999):
            if(diff != temp_diff or count == 1):
                target_pts.append(route[i-1])
                diff = temp_diff
                count = 0
            else:
                count = count+1
        diff = temp_diff
    target_pts.append(route[-1])
    return target_pts

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

algo_mod.set_objects_positions([1,4,10,12,28,37,35,39,42,46,54])

planned_route = algo_mod.find_route(int(sys.argv[1]),int(sys.argv[2]),1,1)
print planned_route

print find_critical_pts(planned_route)
print find_critical_pts_mod(planned_route)
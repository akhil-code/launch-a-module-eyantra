import math
 
def angleof(p,c):
    if(c[0] == p[0] and p[1] > c[1]):
        m = 99999
        angle = math.atan(m)
        angle = math.degrees(angle)
    elif(c[0] == p[0] and p[1] < c[1]):
        m = -99999
        angle = math.atan(m)
        angle = math.degrees(angle)
    elif(p[0] > c[0] and p[1] > c[1]):
        #q4    
        m = (p[1]-c[1])/float((p[0]-c[0]))
        angle = math.atan(m)
        angle = math.degrees(angle)
    elif(p[0] > c[0] and p[1] < c[1]):
        #q1    
        m = (p[1]-c[1])/float((p[0]-c[0]))
        angle = math.atan(m)
        angle = math.degrees(angle)
    elif(p[0] < c[0] and p[1] < c[1]):
        #q2    
        m = (p[1]-c[1])/float((p[0]-c[0]))
        angle = math.atan(m)
        angle = math.degrees(angle)
        angle = angle-180
    elif(p[0] < c[0] and p[1] > c[1]):
        #q3    
        m = (p[1]-c[1])/float((p[0]-c[0]))
        angle = math.atan(m)
        angle = math.degrees(angle)
        angle = angle+180
    else:
        angle = 0

    return angle

#p1:source p2:dest c:centre
def angle_between(p1,p2,c):
    angle1 = angleof(p1,c)
    angle2 = angleof(p2,c)

    angle = angle2-angle1
    if(abs(angle) > 180):
        if(angle < 0):
            angle = 360 - abs(angle)
        elif(angle > 0):
            angle = -(360 - angle)
    return angle


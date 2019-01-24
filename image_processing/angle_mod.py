'''
*Team id: eYRC-LM#448
*Author List: Akhil Guttula, Sai Kiran, Sai Gopal, Mohan
*Filename: angle_mod.py
*Theme: Launch a Module
*Functions: angleof,angle_between
*Global Variables:NULL

'''
#used for mathematical calculations
import math
 
'''
*Function Name: angleof
*Input: point,center
*Output: angle made with horizontal axis
*Logic:angle = arctan(y2-y1/x2-x1)
*Example Call: angleof((60,80),(0,0))
'''
#finds the angle with respect to the x axis using arctan() formula
def angleof(p, c):
    if c[0] == p[0] and p[1] > c[1]:
        m = 99999
        angle = math.atan(m)
        angle = math.degrees(angle)
    elif c[0] == p[0] and p[1] < c[1]:
        m = -99999
        angle = math.atan(m)
        angle = math.degrees(angle)
    elif c[1] == p[1] and p[0] > c[0]:
        angle = 0
    elif c[1] == p[1] and p[0] < c[0]:
        angle = 180
    elif p[0] > c[0] and p[1] > c[1]:
        #q4    
        m = (p[1] - c[1]) / float((p[0] - c[0]))
        angle = math.atan(m)
        angle = math.degrees(angle)
    elif p[0] > c[0] and p[1] < c[1]:
        #q1    
        m = (p[1] - c[1]) / float((p[0] - c[0]))
        angle = math.atan(m)
        angle = math.degrees(angle)
    elif p[0] < c[0] and p[1] < c[1]:
        #q2    
        m = (p[1] - c[1]) / float((p[0] - c[0]))
        angle = math.atan(m)
        angle = math.degrees(angle)
        angle -= 180
    elif p[0] < c[0] and p[1] > c[1]:
        #q3    
        m = (p[1] - c[1]) / float((p[0] - c[0]))
        angle = math.atan(m)
        angle = math.degrees(angle)
        angle += 180
    else:
        angle = 0
    angle = int(angle)
    return angle

'''
*Function Name: angle_between
*Input: point1,point2,center
*Output: angle between the two points along the center
*Logic: angle = angle1(with horizontal axis) - angle2(wiht horizontal axis)
*Example Call: angle_between((70,110),(50,80),(0,0))
'''
#finds the angle between two lines as the differnce in angle made by them w.r.t x-axis
#p1:source p2:dest c:centre
def angle_between(p1, p2, c):
    angle1 = angleof(p1, c)
    angle2 = angleof(p2, c)

    angle = angle2 - angle1
    if abs(angle) > 180:
        if angle < 0:
            angle = 360 - abs(angle)
        elif angle > 0:
            angle = -(360 - angle)
    return angle


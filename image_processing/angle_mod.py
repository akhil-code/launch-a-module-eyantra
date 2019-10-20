'''
* Team id: eYRC-LM#448
* Author List: Akhil Guttula, Sai Kiran, Sai Gopal, Mohan
* Filename: angle_mod.py
* Theme: Launch a Module
* Functions: angleof,angle_between
* Global Variables: NULL
'''


# Used for mathematical calculations
import math


'''
* Finds the angle with respect to the x axis using arctan() formula
* Function Name: angleof
* Input: point,center
* Output: angle made with horizontal axis
* Logic:angle = arctan(y2-y1/x2-x1)
* Example Call: angleof((60,80),(0,0))
'''


def angleof(point, center):
    if center[0] == point[0] and point[1] > center[1]:
        slope = 99999
        angle = math.atan(slope)
        angle = math.degrees(angle)
    elif center[0] == point[0] and point[1] < center[1]:
        slope = -99999
        angle = math.atan(slope)
        angle = math.degrees(angle)
    elif center[1] == point[1] and point[0] > center[0]:
        angle = 0
    elif center[1] == point[1] and point[0] < center[0]:
        angle = 180
    elif point[0] > center[0] and point[1] > center[1]:
        # Quadrant 4
        slope = (point[1] - center[1]) / float((point[0] - center[0]))
        angle = math.atan(slope)
        angle = math.degrees(angle)
    elif point[0] > center[0] and point[1] < center[1]:
        # Quadrant 1
        slope = (point[1] - center[1]) / float((point[0] - center[0]))
        angle = math.atan(slope)
        angle = math.degrees(angle)
    elif point[0] < center[0] and point[1] < center[1]:
        # Quadrant 2
        slope = (point[1] - center[1]) / float((point[0] - center[0]))
        angle = math.atan(slope)
        angle = math.degrees(angle)
        angle -= 180
    elif point[0] < center[0] and point[1] > center[1]:
        # Quadrant 3
        slope = (point[1] - center[1]) / float((point[0] - center[0]))
        angle = math.atan(slope)
        angle = math.degrees(angle)
        angle += 180
    else:
        angle = 0
    angle = int(angle)
    return angle


'''
* Finds the angle between two lines as the difference in angle made by them w.r.t x-axis
* Function name: angle_between
* Input: point1, point2, center
* Output: angle between the two points along the center
* Logic: angle = angle1(with horizontal axis) - angle2(with horizontal axis)
* Example Call: angle_between((70,110),(50,80),(0,0))
'''


def angle_between(source_point, dest_point, common_point):
    angle1 = angleof(source_point, common_point)
    angle2 = angleof(dest_point, common_point)
    angle = angle2 - angle1

    if abs(angle) > 180:
        if angle < 0:
            angle = 360 - abs(angle)
        elif angle > 0:
            angle = -(360 - angle)
    return angle


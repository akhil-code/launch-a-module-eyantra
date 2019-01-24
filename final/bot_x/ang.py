import cv2
import math
import numpy as np

#positive angle in the function angle_between means
#the the angle is toward the vertical downward direction


def angle_of(p,c):
    if(p[0] != c[0]):
        ratio = (p[1]-c[1])/float(p[0]-c[0])
    else:
        ratio = 99999
    ratio = math.atan(ratio)
    ratio = math.degrees(ratio)

    #true
    if(p[0] > c[0]):
        return ratio
        
    #false
    else:
        #q2
        if(p[1] < c[1]):
            return (ratio-180)
        #q3
        else:
            return (ratio+180)

def between(p1,p2,c):
    #POINT-1

    if(p1[0] != c[0]):
        ratio1 = (p1[1]-c[1])/float(p1[0]-c[0])
    else:
        ratio1 = 99999
    ratio1 = math.atan(ratio1)
    ratio1 = math.degrees(ratio1)
    
    #true
    if(p1[0] > c[0]):
        pass
        
    #false
    else:
        #q2
        if(p1[1] < c[1]):
            ratio1 = ratio1-180
        #q3
        else:
            ratio1 = ratio1+180


    #POINT-2

    if(p2[0] != c[0]):
        ratio2 = (p2[1]-c[1])/float(p2[0]-c[0])
    else:
        ratio2 = 99999
    ratio2 = math.atan(ratio2)
    ratio2 = math.degrees(ratio2)
            
    #true
    if(p2[0] > c[0]):
        pass
        
    #false
    else:
        #q2
        if(p2[1] < c[1]):
            ratio2 = ratio2-180
        #q3
        else:
            ratio2 = ratio2+180
    return ratio2-ratio1

'''
p1 = (150,100)
p2 = (100,150)
c = (300,300)

img_src = cv2.imread('test_images/test0.jpg')
cv2.line(img_src,c,p1,(0,0,255),5)
cv2.line(img_src,c,p2,(0,255,0),5)

cv2.imshow('ouput',img_src)

print "1: \t"+str(angleof(p1,c))
print "2: \t"+str(angleof(p2,c))
print "diff: "+ str(angle(p1,p2,c))

cv2.waitKey(0)
cv2.destroyAllWindows()
'''


import cv2, sys
import numpy as np

def nothing(x):
    pass

def getROI(img, pos):
    rows, cols = img.shape
    #finds the row no and column no w.r.t position no
    c = pos % 9
    if c == 0:
        c = 9
        r = pos / 9
    else:    
        r = (pos / 9) + 1
    #finds the starting and ending pixels
    cols_start = (c - 1)*(cols / 9)
    cols_end = c *(cols / 9)
    rows_start = (r - 1) * (rows / 6)
    rows_end = r * (rows / 6)
    #return roi of calculated pixels
    temp_img =  img[rows_start : rows_end, cols_start : cols_end]
    return temp_img


#######################################################################################
row_margin_top = 35
row_margin_bottom = 25
col_margin = 10


# create trackbars for color change
cv2.namedWindow('pallete', cv2.WINDOW_AUTOSIZE)
cv2.createTrackbar('neigh', 'pallete', 32, 40, nothing)

while(True):
    src_img = cv2.imread("testx1.jpg", 0)
    rows, cols = src_img.shape
    src_img = src_img[row_margin_top : rows - row_margin_bottom, col_margin : cols - col_margin]
    
    if cv2.waitKey(100) & 0xFF == ord('q'):
            break
    src_img = getROI(src_img, int(sys.argv[1]))
    
    neigh = cv2.getTrackbarPos('neigh', 'pallete')
    blur  = cv2.bilateralFilter(src_img, 9, 75, 75)
    blur  = cv2.medianBlur(blur, 5)
    
    if(neigh == 0):
        neigh = 1
    th1 = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, (2 * neigh) + 1, 2)
    th2 = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,(2 * neigh) + 1, 2)
    inv  = cv2.bitwise_not(th2)

    cv2.imshow("Source", src_img)
    #cv2.imshow("Adaptive_Mean",th1)
    #cv2.imshow("Adaptive_Gauss",th2)
    cv2.imshow("Inverted", inv)


contours,hierachy = cv2.findContours(inv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
img_temp = np.zeros((512, 512, 3), np.uint8)

for no in range(len(contours)):
    #print cv2.contourArea(contours[no])
    if cv2.contourArea(contours[no]) < 50:
        continue

    cnt = contours[no]
    epsilon = 0.1*cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon, True)
    cv2.drawContours(img_temp, approx, -1, (255, 255, 255), 1)

    #centroid
    M = cv2.moments(contours[no])
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])

    #min area rectangle
    rect = cv2.minAreaRect(contours[no])
    box = cv2.cv.BoxPoints(rect)
    box = np.int0(box)

    try:
        #finding the ratio of areas
        area_ratio = cv2.contourArea(contours[no]) / cv2.contourArea(box)
    except ZeroDivisionError:
        continue
    print 'area ratio: ' + str(area_ratio) + ' \tcontour area: ' + str(cv2.contourArea(contours[no]))

    if area_ratio > 0.90:
        print 'rectangle'
    elif area_ratio > 0.68 and area_ratio <= 0.90:
        print 'circle'
    elif area_ratio < 0.68 and area_ratio > 0.50:
        print 'triangle'

cv2.waitKey(0)
cv2.destroyAllWindows()





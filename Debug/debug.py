import time
import cv2
def LOG(info):
    print("log time:",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime( time.time())))
    print("log info:",info)
    
def SHOW_IMAGE(img):
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
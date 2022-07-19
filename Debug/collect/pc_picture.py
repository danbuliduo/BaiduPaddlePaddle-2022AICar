import cv2
import numpy as np
import datetime
import time
import sys

sys.path.append("../")
from config import *

# 摄像头编号
# cam=0
cam = 0

camera = cv2.VideoCapture(cam)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
btn = 0
if __name__ == "__main__":
    if cam == 0:
        result_dir = "./front_image"
    # cam=1
    else:
        result_dir = "./side_image"
    print("Start!")
    while True:

        return_value, image = camera.read()
        #cv2.imshow("test", image)
        #key = cv2.waitKey(1)
        path = "{}/{}.jpg".format(result_dir, btn)
        btn += 1
        name = "{}.jpg".format(btn)
        print(path)
        cv2.imwrite(path, image)
        time.sleep(0.1)



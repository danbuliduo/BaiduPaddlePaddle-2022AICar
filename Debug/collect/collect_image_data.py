#!/usr/bin/python3
# -*- coding: utf-8 -*-
from joystick import JoyStick
import cv2
import threading
import json
import sys
import time

sys.path.append("../")
sys.path.append("../cart")
from cart.chassis import Chassis
from widgets import *
from config import FRONT_CAM

# 本文件用作无人驾驶车道数据采集
cart = Chassis()


class Logger:

    def __init__(self):
        self.camera = cv2.VideoCapture(FRONT_CAM)
        self.started = False
        self.stopped_ = False
        self.counter = 0
        self.map = {}
        self.result_dir = "train"
        self.error = 0

    def start(self):
        self.started = True
        cart.steer(self.error)

    def pause(self):
        self.started = False
        cart.stop()

    def stop(self):
        if self.stopped_:
            return
        self.stopped_ = True
        cart.stop()
        path = "{}/result.json".format(self.result_dir)
        with open(path, 'w') as fp:
            json.dump(self.map.copy(), fp)
        pass

    def log(self):
        print("error:{}  img_num:{} ".format(self.error, self.counter))
        _, image = self.camera.read()
        self.map[self.counter] = self.error
        path = "{}/{}.jpg".format(self.result_dir, self.counter)
        cv2.imwrite(path, image)
        self.counter += 1
        time.sleep(0.2)


    def stopped(self):
        return self.stopped_


js = JoyStick()
logger = Logger()
b = Buzzer()

def test():
    while not logger.stopped():
        if logger.started:
            logger.log()
    cart.stop()
    
    
def joystick_thread():
    while not logger.stopped():
        _time, value, type_, number = js.read()
        if js.type(type_) == "button":
            print("button:{} state: {}".format(number, value))
            if number == 6:
                if value == 1:
                    logger.start()
                else:
                    logger.pause()
            elif number == 7 and value == 1:
                logger.stop()
        if logger.started:
            if js.type(type_) == "axis" and number == 2:
                print("axis:{} state: {}".format(number, value))
                # handle_axis(_time, value)
                logger.error = value * 1.0 / 32767
                cart.steer(logger.error)
        else:
            cart.stop()
    cart.stop()
    

def main():
    js.open()
    while True:
        b.rings()
        time.sleep(0.2)
        b.rings()
        time.sleep(0.2)
        logger.error = 0
        logger.counter = 0
        logger.stopped_ = False
        cart.speed = 20

        t = threading.Thread(target=joystick_thread, args=())
        t.start()
        test()
        t.join()
        cart.stop()
        
        while True:
            _time, value, type_, number = js.read()
            if number == 11 and value == 1:
                break
            elif number == 10 and value == 1:
                return 0
if __name__ == "__main__":
    # main()
    main()
    for i in range(3):
        b.rings()
        time.sleep(0.2)


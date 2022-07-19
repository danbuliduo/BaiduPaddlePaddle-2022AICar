#!/usr/bin/python3
# -*- coding: utf-8 -*-
# from joystick import JoyStick
import cv2
import threading
import json
import sys
import time

from joystick import *
sys.path.append("../")
sys.path.append("../cart")
from camera import *
from cart.chassis import Chassis
from widgets import *
from config import FRONT_CAM

# 采集程序不要有print函数，会有冲突
DEBUG = 0
# 本文件用作无人驾驶车道数据采集
cart = Chassis()


front_camera = Camera(0, [640, 480])
front_camera.start()
js = JoyStick()
js.open()
b = Buzzer()
def get_mem():
    with open('/proc/meminfo') as fd:
        for line in fd:
            if line.startswith('MemTotal'):
                total = line.split()[1]
                continue
            if line.startswith('MemFree'):
                free = line.split()[1]
                break
    TotalMem = int(total)/1024.0
    FreeMem = int(free)/1024.0
    print( "FreeMem:"+"%.2f" % FreeMem+'M')
    print( "TotalMem:"+"%.2f" % TotalMem+'M')
    
def joy_thread():
    global angle
    global start_flag
    global end_flag
    global reset_flag
    
    while end_flag is not True:
        _time, value, type_, number = js.read()
        if js.type(type_) == "button":
            if DEBUG==1:
                print("time:{}, type:{}, value:{}, number:{}".format(_time,type_,value, number))
            if number == 6:
                if value == 0:
                    start_flag = 0
                else:
                    start_flag = 1
            elif number == 10 and value == 1:
                end_flag = True
            elif number == 11 and value == 1:
                reset_flag = 1
        '''         
            if number ==4 and value == 1:
                angle = 0
            elif number == 3 and value == 1:
                angle -= 0.2
            elif number == 1 and value == 1:
                angle += 0.2
            angle = 1 if angle > 1 else angle
            angle = -1 if angle < -1 else angle
            print(angle)
        '''        
        if js.type(type_) == "axis" and number == 2:
            if start_flag == 1:
                # print("axis:{} state: {}".format(number, value))
                angle = value * 1.0 / 32767
                if DEBUG==1:
                    print(angle)
               
            
def driver_thread():
    global angle
    global start_flag
    global end_flag
    while end_flag is not True:
        if start_flag == 1:
            cart.steer(angle)
        else:
            cart.stop()
        time.sleep(0.005)


class VideoOut:
    def __init__(self):
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.out = cv2.VideoWriter('2.avi', self.fourcc, 15, (640, 480))
        self.frames = []
        self.task = threading.Thread(target=self.write, args=())
        self.task.start()
        
    def open(self, path):
        self.out = self.out.open(path, self.fourcc, 15, (640, 480))
        
    def start_write(self,frames):
        self.frames = frames
        # self.write()
        self.task = threading.Thread(target=self.write, args=())
        self.task.start()
    
    def write(self):

        for frame, error in self.frames:
           self.out.write(frame)
 
    def close(self):
        self.task.join()
        self.out.release()


class PicCache:
    def __init__(self):
        self.counter = 0
        self.result_dir = "train"
        self.roads_data = []
        self.road_json = {}
        self.counter = 0
        self.stoped = False
        self.task = threading.Thread(target=self.save_pic_thread, args=())
        
    def reset(self):
        self.counter = 0
        self.roads_data = []
        self.road_json = {}
    
    def start(self):
        self.task.start()
    
    def save_json(self):
        path = "{}/result.json".format(self.result_dir)
        with open(path, 'w') as fp:
            json.dump(self.road_json.copy(), fp)
            
    def append(self,road_data):
        self.roads_data.append(road_data)
        if DEBUG == 1:
            print(len(self.roads_data))
            get_mem()
    
    def save_pic_thread(self):
        while self.stoped is not True:
            if len(self.roads_data) > 0:
                frame,error = self.roads_data[0]
                path = "{}/{}.jpg".format(self.result_dir, self.counter)
                cv2.imwrite(path, frame)
                if DEBUG == 1:
                    print("save image",self.counter,"ok")
                self.road_json[self.counter] = error
                self.roads_data.pop(0)
                self.counter += 1
                if self.counter % 100 == 0:
                    self.save_json()
    
    def close(self):
        while len(self.roads_data) > 0:
            pass
        self.stoped = True
        self.save_json()
        
                    
class PicOut:
    def __init__(self):
        self.counter = 0
        self.result_dir = "train"
        self.map = {}
        self.frames = []
        self.task = threading.Thread(target=self.write, args=())
        self.task.start()
        self.task_num = 0
        self.counter = 0
    
    def reset(self):
        self.counter = 0
        self.map ={}
        self.frames = []
        
    def save_json(self):
        path = "{}/result.json".format(self.result_dir)
        with open(path, 'w') as fp:
            json.dump(self.map.copy(), fp)
            
    def start_write(self,frames):
        self.frames = frames
        self.task = threading.Thread(target=self.write, args=())
        self.task.start()
        # self.task.join()


    def save(self,frame,error):
        path = "{}/{}.jpg".format(self.result_dir, self.counter)
        cv2.imwrite(path, frame)
        self.map[self.counter] = error
        # print("write:"+str(self.counter))
        self.counter += 1
    
    def write(self):
        # count_t = 0
        for frame, error in self.frames:
            path = "{}/{}.jpg".format(self.result_dir, self.counter)
            cv2.imwrite(path, frame)
            self.map[self.counter] = error
            if DEBUG==1:
                print("write:"+str(self.counter))
            self.counter += 1
            time.sleep(0.05)
 
    def close(self):
        self.task.join()
        path = "{}/result.json".format(self.result_dir)
        with open(path, 'w') as fp:
            json.dump(self.map.copy(), fp)

        
def test_front_video():

    video1 = VideoOut()
    pic = PicOut()
    out_array1 = []
    out_array2 = []
    flag = 0
    counter = 0
    while True:
        img = front_camera.read()

        
        # cv2.imshow("Output", frame)
        if flag == 0:
            out_array1.append(img)
        else:
            out_array2.append(img)
            
        if counter % 200 == 0:
            if flag == 0:
                video1.start_write(out_array1)
                flag = 1
                out_array1 = []
            else:
                video1.start_write(out_array2)
                flag = 0
                out_array2 = []
        if counter > 800:
            break
        counter += 1
        if DEBUG==1:
            print("camera: "+ str(counter))
        
        time.sleep(0.08)
    front_camera.stop()
    video1.close()

    
def pic_test():
    pic = PicOut()
    out_array1 = []
    counter = 0
    while True:
        img = front_camera.read()

        out_array1.append(img)
        if counter % 200 == 0:
            pic.start_write(out_array1)
            flag = 1
            out_array1 = []

        if counter > 800:
            break
        counter += 1
        if DEBUG==1:
            print("camera: "+ str(counter))
        
        time.sleep(0.08)
    front_camera.stop()
    pic.close()
    

        
def main_thread():
    global start_flag
    global angle
    global end_flag
    global reset_flag
    reset_flag = 0
    start_flag = 0
    angle = 0
    counter = 0
    end_flag = False
    result_dir = "train"
    joy = threading.Thread(target=joy_thread, args=())
    cart_thread = threading.Thread(target=driver_thread, args=())
    joy.start()
    cart_thread.start()
    pic = PicOut()

    out_array1 = []
    errors = []
    get_mem()
    while end_flag is not True:
        if reset_flag == 1:
            pic.reset()
            out_array1 = []
            counter = 0
            b.rings()
            time.sleep(0.2)
            reset_flag = 0
            continue
        if start_flag == 1:
            t1 = time.time()
            img = front_camera.read()
            error = angle
            
            out_array1.append((img,error))
            if counter % 200 == 0:
                # get_mem()
                
                pic.start_write(out_array1)
                out_array1 = []
            '''
            pic.save(img,error)
            '''
            counter += 1
            time.sleep(0.08)
            fps = int(1 / (time.time() - t1))
            if DEBUG==1:
                print(fps)
    get_mem()
    pic.start_write(out_array1)
    time.sleep(0.2)
    joy.join()
    front_camera.stop()
    pic.close()
    get_mem()

    
def test_thread():
    global start_flag
    global angle
    global end_flag
    global reset_flag
    reset_flag = 0
    start_flag = 0
    angle = 0
    counter = 0
    end_flag = False
    result_dir = "train"
    joy = threading.Thread(target=joy_thread, args=())
    cart_thread = threading.Thread(target=driver_thread, args=())
    joy.start()
    cart_thread.start()
    pic = PicCache()
    pic.start()

    out_array1 = []
    errors = []
    get_mem()
    while end_flag is not True:
        if reset_flag == 1:
            pic.reset()
            counter = 0
            b.rings()
            time.sleep(0.2)
            reset_flag = 0
            continue
        if start_flag == 1:
            t1 = time.time()
            img = front_camera.read()
            error = angle
            pic.append((img,error))
            counter += 1
            time.sleep(0.08)
            fps = int(1 / (time.time() - t1))
            if DEBUG==1:
                print("fps is :", fps, "counter is:",counter)
    get_mem()
    time.sleep(0.2)
    joy.join()
    front_camera.stop()
    pic.close()
    get_mem()
    
if __name__ == "__main__":
    b.rings()
    time.sleep(0.2)
    b.rings()
    time.sleep(0.2)
    # main_thread()
    test_thread()
    b.rings()
    time.sleep(0.2)
    b.rings()
    time.sleep(0.2)
    
    
    
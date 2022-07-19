#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time

import set_path
from cart.controls import *
from cart.driver import Driver
from detector.detectors import *
from camera import Camera
from config import *
from task import *
from debug import *

import numpy as np
#前、侧摄像头初始化
front_camera = Camera(FRONT_CAM, [640, 480])
side_camera = Camera(SIDE_CAM, [640, 480])
#智能车地盘控制类
driver = Driver()
#模型加载类
cruiser = Cruiser()
# 地面标志检测类
sign_detector = SignDetector()
# 侧边目标物检测类
task_detector = TaskDetector()
# 程序开启运行开关
start_button = Button(1,"UP")
#摄像头伺服电机
servo1 = Servo(1)

STATE_IDLE = "idle"
STATE_CRUISE = "cruise"
STATE_LOCATE_TASK = "sign_detected"
STATE_DO_TASK = "task"

sign_list = [0] * 11
order_num = 1
cam_dir = 1  # 左边为-1，右边为1

# 任务程序开始按钮检测函数
def idle_handler(params=None):
    driver.stop()
    global order_num
    order_num = 1
    LOG("Please press the button")
    while True:
        if start_button.clicked():
            LOG("program start!")
            break
        driver.stop()
    LOG("START!")   
    buzzer.rings()
    time.sleep(0.1)
    return STATE_CRUISE, None


# 按照给定速度沿着道路前进给定的时间
def lane_time(speed, my_time):
    start_time = time.time()
    driver.set_speed(speed)
    while True:
        front_image = front_camera.read()
        error = cruiser.infer_cnn(front_image)
        driver.steer(error)
        timeout = time.time()
        if timeout - start_time > my_time:
            driver.stop()
            break


# 巡航模式
def cruise_handler(params=None):
    global order_num
    # 设置小车巡航速度
    global sign_list
    global cam_dir
    driver.set_speed(FULL_SPEED)
    driver.set_kx(task[order_num]['kx'])
    servo1.servo_control(task[order_num]['angle'], 50)
    time.sleep(0.1)
    print(task[order_num]['angle'])
    if task[order_num]['angle'] > 45:
        cam_dir = -1
    else:
        cam_dir = 1

    while True:
        front_image = front_camera.read()
        angle = cruiser.infer_cnn(front_image)
        driver.steer(angle)
        # 侦测车道上有无标志图标
        res = sign_detector.detect(front_image)
        LOG("res%s"%res)
        if len(res) != 0:
            for sign in res:
                if sign.index == task[order_num]['sign']:

                    sign_list[sign.index] += 1
                    # 连续加测到一定次数，认为检测到，进入到任务定位程序
                    if sign_list[sign.index] > REC_NUM:
                        LOG("res%s"%res)
                        return STATE_LOCATE_TASK, order_num
        else:
            sign_list = [0] * 7
def walk_sign(params):
    is_run = True
    while is_run:
        continue_flag = 0
        front_image = front_camera.read()
            # 计算标签偏移，根据标签前进
        res = sign_detector.detect(front_image)
        if len(res) != 0:
            for sign in res:
                print(sign)
                _x, _y = sign.error_from_center()
                print("from center x is{}, y is {}".format(_x, _y))
                if (sign.box[3] - sign.box[1]) < 160:
                    pass
                    # is_run = False
                if _y > 130:
                    is_run = False
                elif _y < 0:
                    continue_flag = 1
                    continue
                if sign.index == task[params]['sign']:
                    angle = _x / 160
                    driver.steer(angle)
                
        if continue_flag == 1:
            angle = cruiser.infer_cnn(front_image)
            driver.steer(angle)
            
    driver.stop()

# 寻找任务目标
def task_lookfor(params = None):
    time_lookfor = 3
    start_time = time.time()
    find_flag = False
    while find_flag is not True:
        side_image = side_camera.read()
        res_side = task_detector.detect(side_image)
        if len(res_side) > 0:
            print(res_side)
            for res in res_side:
                if res.index in task[params]['index']:
                    # 标签到一定位置退出循环  
                    _x, _y = res.error_from_point(task_functions[res.index]['position'])
                    _x = _x * cam_dir
                    print("find task,distance is:", _x)
                    if task_functions[res.index]['location'] == False:
                        # 不需要定位直接做任务
                        print("do not location ")
                        return res.index
                    else:
                        driver.run(10,10)
                    if _x > POSITION_THRESHOLD:
                        driver.run(-10, -10)
                        return res.index
                    elif _x > 0-POSITION_THRESHOLD:
                        return res.index
        else:
            front_image = front_camera.read()
            angle = cruiser.infer_cnn(front_image)
            driver.steer(angle)
        current_time = time.time()
        # 长时间未到达位置
        if current_time - start_time > LOCATE_TIME:
            return None 
            
def location_ok(params = None):
    start_time = time.time()
    location_flag = False
    while location_flag is not True:
        side_image = side_camera.read()
        res_side = task_detector.detect(side_image)
        if len(res_side) > 0:
            for res in res_side:
                if res.index in task[params]['index']:
                    # 标签到一定位置退出循环
                    _x, _y = res.error_from_point(task_functions[res.index]['position'])
                    _x = _x * cam_dir
                    print(_x)
                    if _x < 0-POSITION_THRESHOLD:
                        print("front")
                        driver.run(10, 10)
                    elif _x > POSITION_THRESHOLD:
                        print("back")
                        driver.run(-10, -10)
                    else:
                        driver.stop()
                        print("location ok")
                        return STATE_DO_TASK, res.index
        current_time = time.time()
        # 长时间未到达位置
        if current_time - start_time > 3:
            return STATE_CRUISE, None
        
    
def locate_task_handler(params=None):
    global order_num
    global cam_dir
    LOG("Def locate_task_handler(params):%s"%params)
    walk_sign(params)
    
    if params == 1 or params==8:
        order_num += 1
        print("ready to do task")
        return STATE_DO_TASK, task[params]['index'][0]
    adjust_angle()

    if task[params]['check'] is not True:
        order_num += 1
        print("ready to do task")
        return STATE_DO_TASK, task[params]['index'][0]
        
    print("sign location ok!")        
    order_num += 1
    if task[params]['location']:
        driver.set_speed(15)
        print("speed is 15")
    else:
        driver.set_speed(20)
        print("speed is 20")
    driver.steer(0)
    
    
        
    if order_num > 11:
        order_num = 11

    print("looking for task")
    index = task_lookfor(params)
    if task_functions[index]['location'] == False:
        return STATE_DO_TASK, index
    print("find task!")
    location_ok(params)
    return STATE_DO_TASK, index

        



# 做任务
def do_task_handler(params=None):
    LOG("Def do_task_handler params:%s %s"%(str(params),task_functions[params]))
    if params == 1:  # alamutu 阿拉木图
        driver.stop()
        task_castle("alamutu")

    elif params == 2:  # bad_person1
        LOG("TASK 6")
        driver.stop()
        time.sleep(4)
        

    elif params == 3:  # bad_person2
        LOG("TASK 6")
        driver.stop()
        time.sleep(4)

    elif params == 4:  # dunhuang
        driver.stop()
        task_castle("dunhuang")

    elif params == 5:  # friendship
        driver.stop()
        time.sleep(4)
        
    elif params == 6:  # goodperson1
        LOG("TASK 6")
        lane_time(30,1.5)

    elif params == 7:  # goodperson2
        LOG("TASK 6")
        lane_time(30,1.5)

    elif params == 8:  # jstdb
        driver.stop()
        task_castle("jstdb")

    elif params == 9:  # purchase
        driver.stop()
        while True:
            img = side_camera.read()
            frameBGR = cv2.GaussianBlur(img, (7, 7), 0)
            hsv = cv2.cvtColor(frameBGR, cv2.COLOR_BGR2HSV)
            colorLow = np.array(HSV_GREEN[0:3])
            colorHigh = np.array(HSV_GREEN[3:6])
            mask = cv2.inRange(hsv, colorLow, colorHigh)
            kernal = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernal)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernal)
            ret, thresh = cv2.threshold(mask,127,255,0)
            M = cv2.moments(thresh)
            cX = int(M["m10"] / M["m00"])
            print("centerX:%s"%cX)
            if (cX>450):
                if(cX > 480): 
                    driver.run(-12,-12)
                    time.sleep(0.2)
                else:
                    driver.run(-8,-8)
                    time.sleep(0.1)
                driver.stop()
            elif(cX<440):
                if (cX<410):
                    driver.run(12,12)
                    time.sleep(0.2)
                else:
                    driver.run(8,8)
                    time.sleep(0.1)
                driver.stop()
            else : break
        task_purchase()


    elif params == 10:  # trade
        driver.run(-13, -13)
        time.sleep(1.8)
        driver.stop()
        trade_good()

        driver.run(13, 13)
        time.sleep(1.8)
        driver.stop()
        trade_good_1()
        
        driver.run(13, 13)
        time.sleep(1.2)
        driver.stop()
        trade_good_over()
        

    elif params == 11:  # seesaw
        lane_time(30,2)

    return STATE_CRUISE, None

def adjust_angle():
    while True:
        frame = front_camera.read()
        angle = cruiser.infer_cnn(frame)
        LOG("Def - adjust_angle:%s"%angle)
        if angle < -0.01:
            driver.run(0, 15)
        elif angle > 0.01:
            driver.run(15, 0)
        else:
            driver.stop()
            return

state_map = {
    STATE_IDLE: idle_handler,
    STATE_CRUISE: cruise_handler,
    STATE_LOCATE_TASK: locate_task_handler,
    STATE_DO_TASK: do_task_handler,
}

if __name__ == '__main__':
    #摄像头初始化
    front_camera.start()
    side_camera.start()
    # 基准速度与转弯系数
    driver.set_speed(40)
    driver.set_kx(1)
    #初始任务编号
    order_num = 1
    params = None
    time.sleep(0.1)
    #task_init()
    # 延时
    time.sleep(0.1)
    #电机省电关闭
    startmachine()
    buzzer.rings()
    #按键启动
    idle_handler()
    debugindex = 0
    while True:
        debugindex+=1
        LOG("This is Main While, COUNT:%d"%debugindex)
        _, params = cruise_handler(order_num)
        _, params = locate_task_handler(params)
        _, params = do_task_handler(params)
        driver.stop()

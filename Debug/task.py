#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 导入当前目录下的文件夹作为路径
import set_path
from cart.controls import *
from cart.roboticarm import RoboticARM
import time

#---------------Debug ADD--------------
buzzer = Buzzer()
robotic_arm = RoboticARM(True)

def task_purchase():
    robotic_arm.setNode3(60,20)
    time.sleep(1)
    robotic_arm.setNode2(120,20)
    time.sleep(1)
    robotic_arm.setNodeClaws(20,15)
    time.sleep(1)
    robotic_arm.setNode2(130,1)
    time.sleep(1)
    robotic_arm.setNodeClaws(32,15)
    time.sleep(0.5)
    robotic_arm.setNode2(80)
    time.sleep(1)
    
    robotic_arm.initPobotic(False)
    
    robotic_arm.setNode1(125,40)
    time.sleep(1)
    robotic_arm.setNode3(100,40)
    time.sleep(0.8)
    robotic_arm.setNode2(80)
    time.sleep(0.8)

light = Light(2)
def task_castle(flagname):
    if flagname == "dunhuang":
       servo_raise.servo_control(-40, 60)
    elif flagname == "jstdb":
        servo_raise.servo_control(-120, 60)
    elif flagname == "alamutu":
        servo_raise.servo_control(120, 60)
    time.sleep(1)
    for i in range(0,3):
        light_work("green",0.25)
        time.sleep(0.25)
    servo_raise.servo_control(40, 60)
    time.sleep(1)
def light_work(color, tim_t):
    red = [80, 0, 0]
    green = [0, 80, 0]
    yellow = [80, 80, 0]
    off = [0, 0, 0]
    light_color = [0, 0, 0]
    if color == 'red':
        light_color = red
    elif color == 'green':
        light_color = green
    elif color == 'yellow':
        light_color = yellow
    light.light_control(0, light_color[0], light_color[1], light_color[2])
    time.sleep(tim_t)
    light.light_off()
#---------------Debug ADD--------------

motor_LR = Motor_rotate(2, 1)   # 左右移动电机
motor_UD = Motor_rotate(2, 2)   # 上下移动电机

magsens = Magneto_sensor(3)     # 磁感应
limit_switch = LimitSwitch(4)   # 限位开关

servo_shot = Servo_pwm(1)       # 击打伺服
servo_grasp = Servo_pwm(2)      # 抓手伺服


servo_raise = Servo(2)

def task_init():
    print("task init ...")
    servo_shot.servo_control(170, 80)   # 收回
    servo_grasp.servo_control(180, 70)  # 关闭抓手
    task_lowest()
    time.sleep(0.5)
    
def task_init_reverse():
    print("task init ...")
    servo_shot.servo_control(160, 80)   # 收回
    servo_grasp.servo_control(180, 70)  # 关闭抓手
    while limit_switch.clicked() is not True:
        motor_UD.motor_rotate(100)
    time.sleep(0.05)
    motor_UD.motor_rotate(0)
    time.sleep(0.5)
    
# 下降到最低
def task_lowest():
    while limit_switch.clicked() is not True:
        motor_UD.motor_rotate(-100)
    time.sleep(0.05)
    motor_UD.motor_rotate(0)
    

def task_down():
    while True:
        kl = magsens.read()
        if kl != None and kl >= 70:
            break
        motor_UD.motor_rotate(-100)
    time.sleep(0.05)
    motor_UD.motor_rotate(0)
    
def task_up():
    print("up ...")
    while True:
        kl = magsens.read()
        if kl != None and kl >= 70:
            break
        motor_UD.motor_rotate(100)
    time.sleep(0.05)
    motor_UD.motor_rotate(0)
    print("up ok!")



def move_LR(speed_m, time_m):
    motor_LR.motor_rotate(speed_m)
    time.sleep(time_m)
    motor_LR.motor_rotate(0)
    
def move_UD(speed_m, time_m):
    motor_UD.motor_rotate(speed_m)
    time.sleep(time_m)
    motor_UD.motor_rotate(0)



 
def purchase_good():
    
    task_up()   # 上升到磁感应
    servo_grasp.servo_control(100, 90)   # 打开抓手
    time.sleep(0.4)
    move_LR(-60, 1.4)   # 放出
    servo_grasp.servo_control(180, 70)  # 抓住
    time.sleep(1)
    move_UD(90,1.8) # 上升一些
    move_LR(80, 1.8)  # 收回
    time.sleep(0.5)
    task_lowest()   # 购物完成后下降



def raise_flag(flagname):
    print("raise_flag", flagname,  "start!")
    if flagname == "dunhuang":
        # dunhuang
        servo_raise.servo_control(-40, 60)
        time.sleep(1)
        for i in range(0, 3):
            light_work("green", 0.1)
    elif flagname == "jstdb":
        # jstdb
        servo_raise.servo_control(-120, 60)
        time.sleep(1)
        for i in range(0, 3):
            light_work("green", 0.1)
    elif flagname == "alamutu":
        # almutu
        servo_raise.servo_control(122, 60)
        time.sleep(1)
        for i in range(0, 3):
            light_work("green", 0.1)

    servo_raise.servo_control(42, 60)
    # time.sleep(2)
    print("raise_flag stop!")

def friendship():
    print("friendship start!")
    for i in range(3):
        # print(i)
        light_work("red", 0.2)
        buzzer.rings()
        time.sleep(0.4)
    
def shot_target():
    print("shot_target1 start!")
    task_up() # 上升到磁感应
    move_LR(-50, 0.55)
    move_UD(100, 2)
    time.sleep(0.2)
    servo_shot.servo_control(30, 80)    # 击打
    time.sleep(1.5)
    servo_shot.servo_control(170, 80)   # 收回
    time.sleep(0.5)
    task_down()
    move_LR(50, 1)
    task_lowest()
    motor_UD.motor_rotate(0)
    print("shot_target stop!")


def shot_target2():
    print("shot_target2 start!")

    task_up() # 上升到磁感应
    move_UD(100, 0.5)
    time.sleep(0.2)
    servo_shot.servo_control(30, 80)    # 击打
    time.sleep(1.5)
    servo_shot.servo_control(170, 80)   # 收回
    time.sleep(0.5)
    task_lowest()
    motor_UD.motor_rotate(0)
    print("shot_target stop!")


def trade_good_1():
    print("trade_good_1 start!")
    # 以货易货1层
    move_UD(100, 1)
    move_LR(-50, 0.8) # 伸出抓手
    servo_grasp.servo_control(180, 70) # 闭合抓手
    time.sleep(1.0)
    move_UD(100, 0.8)
    move_LR(50, 2.3) # 收回抓手


def trade_good_2():
    print("trade_good_2 start!")
    # 以货易货2层
    task_up()
    move_LR(-50, 0.5) # 稍微伸出抓手
    move_UD(100, 1)
    task_up()
    move_LR(-50, 1.5) # 伸出抓手
    servo_grasp.servo_control(180, 70) # 闭合抓手
    time.sleep(1.0)
    move_UD(100, 0.8)
    move_LR(50, 1.5) # 收回抓手


def trade_good_over():
    task_lowest()
    move_UD(100, 1)
    move_LR(50,1.5)
    task_lowest()
    
    
def trade_good():
    # 以货易货即将开始
    move_UD(100, 1)
    move_LR(-50, 1.5) # 稍伸抓手
    servo_grasp.servo_control(70, 90)# 张开抓手
    time.sleep(1.0)
    move_LR(50, 2.3) # 收回抓手
    time.sleep(0.8)
    servo_grasp.servo_control(50, 90)    # 张开抓手
    time.sleep(1.0)




if __name__ == '__main__':
    print("test")
    task_purchase()
    task_castle("jstdb")
    pass
    #servo_grasp.servo_control(170, 90)
    # friendship()
    # task_init()
    # task_init_reverse()
    #purchase_good()
    # time.sleep(0.5)
    # trade_good_1()
    # trade_good_2()
    # shot_target()
    # shot_target()
    # purchase_good()
    # trade_good()
    # time.sleep(3)
    # trade_good_2()
    # trade_good_over()
    # raise_flag(2, 3, "dunhuang")  
    # time.sleep(1)
    # raise_flag(2, 3, "alamutu")
    # time.sleep(1)
    # raise_flag(2,3,"jsddb")
    # while True:
    #     light_work(3,"green",0.2)

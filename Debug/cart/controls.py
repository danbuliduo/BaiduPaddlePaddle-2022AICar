#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import struct
from serial_port import serial_connection

serial = serial_connection


# 机器省电关闭
def startmachine():
    cmd_data = bytes.fromhex('77 68 03 00 02 67 0A')
    for i in range(0, 2):
        serial.write(cmd_data)
        time.sleep(0.2)


class Button:
    def __init__(self, port, buttonstr):
        self.state = False
        self.port = port
        self.buttonstr = buttonstr
        port_str = '{:02x}'.format(port)
        self.cmd_data = bytes.fromhex('77 68 05 00 01 E1 {} 01 0A'.format(port_str))

    def clicked(self):
        serial.write(self.cmd_data)
        response = serial.read()
        buttonclick="no"
        if len(response) == 9 and  response[5]==0xE1 and response[6]==self.port:
            button_byte=response[3:5]+bytes.fromhex('00 00')
            button_value=struct.unpack('<i', struct.pack('4B', *(button_byte)))[0]
            if button_value>=0x1f1 and button_value<=0x20f:
                buttonclick="UP"
            elif button_value>=0x330 and button_value<=0x33f:
                buttonclick = "LEFT"
            elif button_value>=0x2f1 and button_value<=0x30f:
                buttonclick = "DOWN"
            elif button_value>=0x2a0 and button_value<=0x2af:
                buttonclick = "RIGHT"
            else:
                buttonclick
        return self.buttonstr==buttonclick

class Button_angel:
    BUTTON = {"1": "01", "2": "02", "3": "03", "4": "04"}

    def __init__(self, port, button):
        self.state = False
        self.port = port
        button_str = self.BUTTON[button]
        port_str = '{:02x}'.format(port)
        self.cmd_data = bytes.fromhex('77 68 05 00 01 DB {} {} 0A'.format(port_str, button_str))

    def clicked(self):
        serial.write(self.cmd_data)
        response = serial.read()
        # print("resp=",len(response))
        if len(response) == 8 and response[4] == 0xDB and response[5] == self.port:
            button_byte = response[3]
            # print("button_byte=%x"%button_byte)
            if button_byte == 0x01:
                return True
        return False


class LimitSwitch:
    def __init__(self, port):
        self.state = False
        self.port = port
        self.state = True
        port_str = '{:02x}'.format(port)
        # print (port_str)
        self.cmd_data = bytes.fromhex('77 68 04 00 01 DD {} 0A'.format(port_str))

    def clicked(self):
        serial.write(self.cmd_data)
        response = serial.read()  # 77 68 01 00 0D 0A
        if len(response) < 8 or response[4] != 0xDD or response[5] != self.port \
                or response[2] != 0x01:
            return False
        state = response[3] == 0x01
        # print("state=",state)
        # print("elf.state=", self.state)
        clicked = False
        if state == True and self.state == True and clicked == False:
            clicked = True
        if state == False and self.state == True and clicked == True:
            clicked = False
        # print('clicked=',clicked)
        return clicked

#超声波
class UltrasonicSensor():
    def __init__(self, port):
        self.port = port
        port_str = '{:02x}'.format(port)
        self.cmd_data = bytes.fromhex('77 68 04 00 01 D1 {} 0A'.format(port_str))

    def read(self):
        serial.write(self.cmd_data)
        # time.sleep(0.01)
        return_data = serial.read()
        if len(return_data)<11 or return_data[7] != 0xD1 or return_data[8] != self.port:
            return None
        # print(return_data.hex())
        return_data_ultrasonic = return_data[3:7]
        ultrasonic_sensor = struct.unpack('<f', struct.pack('4B', *(return_data_ultrasonic)))[0]
        # print(ultrasonic_sensor)
        return int(ultrasonic_sensor)


class Servo:
    def __init__(self, ID):
        self.ID = ID
        self.ID_str = '{:02x}'.format(ID)

    def servo_control(self, angle, speed):
        angle = int(angle)
        cmd_servo_data = bytes.fromhex('77 68 08 00 02 36 {}'.format(self.ID_str)) + speed.to_bytes(1, byteorder='big',
                                                                                                    signed=True) + \
                         (angle).to_bytes(3, byteorder='little', signed=True) \
                         + bytes.fromhex('0A')

        serial.write(cmd_servo_data)


class Servo_pwm:
    def __init__(self, ID):
        self.ID = ID
        self.ID_str = '{:02x}'.format(ID)

    def servo_control(self, angle, speed):
        cmd_servo_data = bytes.fromhex('77 68 06 00 02 0B') + bytes.fromhex(self.ID_str) + speed.to_bytes(1,
                                                                                                          byteorder='big',
                                                                                                          signed=True) + \
                         angle.to_bytes(1, byteorder='big', signed=False) + bytes.fromhex('0A')
        # for i in range(0,2):
        serial.write(cmd_servo_data)
        # time.sleep(0.3)

class Light:
    def __init__(self, port):
        self.port = port
        self.port_str = '{:02x}'.format(port)

    def light_control(self, which, Red, Green, Blue):  # 0代表全亮，其他值对应灯珠亮，1~4
        which_str = '{:02x}'.format(which)
        Red_str = '{:02x}'.format(Red)
        Green_str = '{:02x}'.format(Green)
        Blue_str = '{:02x}'.format(Blue)
        cmd_servo_data = bytes.fromhex('77 68 08 00 02 3B {} {} {} {} {} 0A'.format(self.port_str, which_str, Red_str \
                                                                                    , Green_str, Blue_str))
        serial.write(cmd_servo_data)

    def light_off(self):
        cmd_servo_data1 = bytes.fromhex('77 68 08 00 02 3B 02 00 00 00 00 0A')
        cmd_servo_data2 = bytes.fromhex('77 68 08 00 02 3B 03 00 00 00 00 0A')
        cmd_servo_data = cmd_servo_data1 + cmd_servo_data2
        serial.write(cmd_servo_data)


class Motor_rotate:
    def __init__(self, id, port):
        self.port = port
        self.id = id
        self.id_str = '{:02x}'.format(id)
        self.port_str = '{:02x}'.format(port)

    #
    def motor_rotate(self, speed):
        cmd_servo_data = bytes.fromhex('77 68 06 00 02 0C') + bytes.fromhex(self.id_str) + bytes.fromhex(
            self.port_str) + \
                         speed.to_bytes(1, byteorder='big', signed=True) + bytes.fromhex('0A')
        serial.write(cmd_servo_data)


class Infrared_value:
    def __init__(self, port):
        port_str = '{:02x}'.format(port)
        self.cmd_data = bytes.fromhex('77 68 04 00 01 D4 {} 0A'.format(port_str))

    def read(self):
        serial.write(self.cmd_data)
        return_data = serial.read()
        if return_data[2] != 0x04:
            return None
        if return_data[3] == 0x0a:
            return None
        return_data_infrared = return_data[3:7]
        print(return_data_infrared)
        infrared_sensor = struct.unpack('<i', struct.pack('4B', *(return_data_infrared)))[0]
        return infrared_sensor

#蜂鸣器
class Buzzer:
    def __init__(self):
        self.cmd_data = bytes.fromhex('77 68 06 00 02 3D 03 02 0A')

    def rings(self):
        serial.write(self.cmd_data)


class Magneto_sensor:
    def __init__(self, port):
        self.port = port
        port_str = '{:02x}'.format(self.port)
        self.cmd_data = bytes.fromhex('77 68 04 00 01 CF {} 0A'.format(port_str))

    def read(self):
        serial.write(self.cmd_data)
        return_data = serial.read()
        # print("return_data=",return_data[8])
        if len(return_data) < 11 or return_data[7] != 0xCF or return_data[8] != self.port:
            return None
        # print(return_data.hex())
        return_data = return_data[3:7]
        mag_sensor = struct.unpack('<i', struct.pack('4B', *(return_data)))[0]
        # print(ultrasonic_sensor)
        return int(mag_sensor)


class Test:
    pass

if __name__ == '__main__':
    on_off_button = LimitSwitch(1)
    button_2 = Button(1, "2")
    button_4 = Button(1, "4")
    button_1 = Button(1, "1")
    button_3 = Button(1, "3")
    button_new_2 = Button_angel(1, "2")
    button_new_4 = Button_angel(1, "4")
    button_new_1 = Button_angel(1, "1")
    button_new_3 = Button_angel(1, "3")
    motor = Motor_rotate(2, 1)
    removemotor = Motor_rotate(2, 2)
    servo1 = Servo(1)
    servo2 = Servo(2)
    ultr_sensor = UltrasonicSensor(4)
    servo3 = Servo_pwm(1)
    servo4 = Servo_pwm(2)
    limit_switch = LimitSwitch(4)
    magsens = Magneto_sensor(3)
    buzzer = Buzzer()
    servo1 = Servo(5)
    motor.motor_rotate(-40)
    
    while True:
        print("button_1={},button_2={},button_3={},button_4={} ".format(button_1.clicked(),button_2.clicked(),button_3.clicked(),button_4.clicked()))
        print("button_new_1={},button_new_2={},button_new_3={},button_new_4={}".format(button_new_1.clicked(), button_new_2.clicked(), button_new_3.clicked(), button_new_4.clicked()))
        cg = magsens.read()
        print("------------------>>Magneto_sensor=", cg)
        distance = ultr_sensor.read()
        print("------------------>>distance=", distance)
        time.sleep(1)
    # while True:
    #     buzzer.rings()
    #     time.sleep(0.1)
    # time.sleep(1)
    # servo2.servo_control(45, 40)
    # servo1.servo_control(100, 50)
    time.sleep(1)
    motor.motor_rotate(0)
    # time.sleep(3)
    # servo1.servo_control(-50, 50)
    # time.sleep(3)
    # servo1.servo_control(120, 50)
    # time.sleep(3)
    # while True:
    #     servo1.servo_control(0,50)
    #     time.sleep(3)
    #     servo1.servo_control(150,50)
    #     time.sleep(3)
    #     servo1.servo_control(0, 50)
    #     time.sleep(3)
    #     servo1.servo_control(-150,50)
    #     time.sleep(3)
    # removemotor = Motor_rotate(1)
    # mk =SerialAssistant()
    # mk.start_port()
    # time.sleep(1)
    # while True:
    #     buzzer.rings()
    #     time.sleep(0.5)
    # while True:
    #     print(limit_switch.clicked())
    #     time.sleep(0.1)
    # while True:
    # 手抓电机
    # motor.motor_rotate(60)
    # time.sleep(0.05)
    # motor.motor_rotate(-50)
    # time.sleep(0.05)
    # motor.motor_rotate(0)
    # 抬升电机

    # removemotor.motor_rotate(60)
    # time.sleep(6)
    # removemotor.motor_rotate(0)
    # removemotor.motor_rotate(60)
    # time.sleep(12)
    # removemotor.motor_rotate(0)
    #     removemotor.motor_rotate(60)
    #     while True:
    #         if limit_switch.clicked():
    #             time.sleep(0.05)
    #             removemotor.motor_rotate(0)
    #             break
    #     removemotor.motor_rotate(-60)
    #     time.sleep(11)
    # while True:
    #     # print(limit_switch.clicked())
    #     distance=ultr_sensor.read()
    #     print("------------------>>distance=",distance)
    # removemotor.motor_rotate(-100)
    # time.sleep(6)
    # removemotor.motor_rotate(0)
    # while True:
    #     km=magsens.read()
    #     print(km)
    #     time.sleep(0.2)
    # while True:
    # 手抓
    # servo3.servo_control(50,70)
    # print("aaaaaa")
    # time.sleep(2)
    # servo3.servo_control(180,70)
    # print("bbbbbb")
    # time.sleep(2)
    # #推杆
    # servo4.servo_control(0,50)
    # print("cccccc")
    # time.sleep(2)
    # servo4.servo_control(180,50)
    # print("dddddd")
    # time.sleep(2)
    #
    # servo1.servo_control(-85, 30)
    # mk.handler()
    # 摄像头0~130
    # while True:
    #     print("+++++++++==========>>>>>")
    #     print("1")
    #     servo2.servo_control(90, 50)
    #     time.sleep(3)
    #     print("2")
    #     servo2.servo_control(0, 50)
    #     time.sleep(3)
    

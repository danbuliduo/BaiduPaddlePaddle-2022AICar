#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import serial
import sys
sys.path.append("../")
from config import CONTROLLER


comma_head_01_motor = bytes.fromhex('77 68 06 00 02 0C 01 01')
comma_head_02_motor = bytes.fromhex('77 68 06 00 02 0C 01 02')
comma_head_03_motor = bytes.fromhex('77 68 06 00 02 0C 01 03')
comma_head_04_motor = bytes.fromhex('77 68 06 00 02 0C 01 04')
comma_head_all_motor = bytes.fromhex('77 68 0c 00 02 7a 01')
comma_trail = bytes.fromhex('0A')


def speed_limit(speeds):
    i = 0
    for speed in speeds:
        if speed > 100:
            speed = 100
        elif speed < -100:
            speed = -100
        speeds[i] = speed
        i = i + 1
    return speeds


class Chassis:
    """
    底盘控制
    """

    def __init__(self):
        """
        :rtype: object
        """
        self.speed = 20
        self.kx = 0.85
        portx = "/dev/ttyUSB0"
        if CONTROLLER == "mc601":
            bps = 380400
        elif CONTROLLER == "wobot":
            bps = 115200
        else:
            bps = 115200
        self.serial = serial.Serial(portx, int(bps), timeout=0.0005, parity=serial.PARITY_NONE, stopbits=1)
        self.p = 0.8
        self.slow_ratio = 0.97
        self.min_speed = 20

    def steer(self, angle):
        # print(angle)
        speed = int(self.speed)
        delta = angle * self.kx
        left_wheel = speed
        right_wheel = speed
    
        if delta < 0:
            left_wheel = int((1 + delta) * speed)
        elif delta > 0:
            right_wheel = int((1 - delta) * speed)
        self.move([left_wheel, right_wheel, left_wheel, right_wheel])

    def stop(self):
        self.move([0, 0, 0, 0])

    def exchange(self, speed):
        if speed > 100:
            speed = 100
        elif speed < -100:
            speed = -100
        else:
            speed = speed
        return speed
    
    def move(self, speeds):
        left_front = int(speeds[0])
        right_front = -int(speeds[1])
        left_rear = int(speeds[2])
        right_rear = -int(speeds[3])
        self.min_speed = int(min(speeds))

        left_front=self.exchange(left_front)
        right_front = self.exchange(right_front)
        left_rear = self.exchange(left_rear)
        right_rear = self.exchange(right_rear)
        
        left_front_kl = comma_head_01_motor + left_front.to_bytes(1, byteorder='big', signed=True) + comma_trail
        right_front_kl = comma_head_02_motor + right_front.to_bytes(1, byteorder='big', signed=True) + comma_trail
        left_rear_kl = comma_head_03_motor + left_rear.to_bytes(1, byteorder='big', signed=True)+ comma_trail
        right_rear_kl = comma_head_04_motor + right_rear.to_bytes(1, byteorder='big', signed=True)+ comma_trail

        self.serial.write(left_front_kl)
        self.serial.write(right_front_kl)
        self.serial.write(left_rear_kl)
        self.serial.write(right_rear_kl)

        time.sleep(0.001)

    def turn_left(self):
        speed = self.speed
        left_wheel = -speed
        right_wheel = speed
        self.move([left_wheel, right_wheel, left_wheel, right_wheel])

    def turn_right(self):
        speed = self.speed
        left_wheel = speed
        right_wheel = -speed

        self.move([left_wheel, right_wheel, left_wheel, right_wheel])

    def reverse(self):
        speed = self.speed
        self.move([-speed, -speed, -speed, -speed])


def test():
    c = Chassis()
    while True:
        c.move([20, 20, 20, 20])
        time.sleep(4)
        c.stop()
        time.sleep(1)


if __name__ == "__main__":
    print("test")
    test()
#!/usr/bin/python3
# -*- coding: utf-8 -*-

FRONT_CAM = 0   # 前摄像头编号
SIDE_CAM = 1    # 边摄像头编号

task = {
        1:{"label":"采购货物", "angle":-40, "check":True, "location":True, "sign":4, "index":[9], "kx":0.9},
        2:{"label":"文化交流", "angle":125, "check":True, "location":True, "sign":1, "index":[1, 4, 8], "kx":1},
        3:{"label":"守护丝路", "angle":125, "check":True, "location":True, "sign":3, "index":[2, 3, 6, 7], "kx":0.7},
        4:{"label":"守护丝路", "angle":125, "check":True, "location":False, "sign":3, "index":[2, 3, 6, 7], "kx":0.7},
        5:{"label":"放歌友谊", "angle":125, "check":False, "location":False, "sign":2, "index":[5], "kx":0.7},
        6:{"label":"守护丝路", "angle":125, "check":True, "location":False, "sign":3, "index":[2, 3, 6, 7], "kx":1},
        7:{"label":"文化交流", "angle":125, "check":True, "location":True, "sign":1, "index":[1, 4, 8], "kx":1 },
        8:{"label":"翻山越岭", "angle":125, "check":False, "location":False, "sign":5,"index":[11], "kx":1},
        9:{"label":"文化交流", "angle":125, "check":True, "location":False, "sign":1, "index":[1, 4, 8], "kx":1},
        10:{"label":"以物易物", "angle":-40, "check":True, "location":False, "sign":6, "index":[10], "kx":1},
        11:{"label":"守护丝路", "angle":-40, "check":True, "location":False, "sign":3,"index":[2, 3, 6, 7], "kx":1},
}
        
task_functions = {
        1:{"label":"alamutu","location":False, "position":[155,340]}, # 位置7 阿拉木图
        2:{"label":"badperson1","location":True, "position":[55, 158]}, # 位置10 坏人1
        3:{"label":"badperson2","location":True, "position":[580, 158]}, # 位置3 坏人2
        4:{"label":"dunhuang","location":False, "position":[480,340]},  # 位置2 敦煌
        5:{"label":"friendship","location":False, "position":[]},   #位置5 放歌友谊
        6:{"label":"goodperson1","location":False, "position":[600, 250]},    # 位置4 好人1
        7:{"label":"goodperson2","location":False, "position":[615, 250]},    # 位置6 好人2
        8:{"label":"jstdb","location":False, "position":[480, 340]},  # 位置8 君士坦丁堡
        9:{"label":"purchase","location":True, "position":[240,340]},    # 位置1  采购货物
        10:{"label":"trade","location":True, "position":[230,100]},  # 位置9  以货易货
        11:{"label":"seesaw","location":False, "position":[]},  # 位置9 翻山越岭
}
#----开发板型号设置----
# CONTROLLER = "mc601"
CONTROLLER = "wobot"

REC_NUM = 3    # 图标出现次数而统计确认识别结果

POSITION_THRESHOLD = 10     # 位置偏差阈值

HIGH_SPEED = 40         # 高速速度
FULL_SPEED = 30         # 中速速度
SLOW_SPEED = 16         # 慢速速度，加速速度
ACCELERATION_TIME = 3   # 启动时间

SIGN_LOCATE_TIME = 1.4
LOCATE_TIME = 100

sign_label = {"background": 1, "castle": 1, "friendship": 1, "guard": 1, "purchase": 1, "seesaw":1, "trade": 1}
TASK_LIST = []
TASK_LABEL = ["background", "alamutu", "badperson", "badperson2", "dunhuang", "friendship", "goodperson", "goodperson2", "jstdb", "purchase", "trade"]
#--------------ADD:
HSV_GREEN = [42, 45, 128, 93, 255, 255]
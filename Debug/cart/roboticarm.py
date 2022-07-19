import time
from controls import Servo_pwm


class RoboticARM:
    def __init__(self, initClass=True):
        self.servo_node1 = Servo_pwm(2)
        self.servo_node2 = Servo_pwm(3)
        self.servo_node3 = Servo_pwm(4)
        self.servo_node4 = Servo_pwm(5)
        self.servo_claws = Servo_pwm(6)

        if initClass :
            self.initPobotic(True)

        #self.setNodeClaws(40)
        #time.sleep(0.5)
        self.setNode2(80)
        time.sleep(0.8)
        self.setNode3(100,40)
        time.sleep(0.8)
        #self.setNode1(0)
        #time.sleep(0.8)
        
    def initPobotic(self,work=True):
        if(work):
            self.setNodeClaws(40)
            time.sleep(0.8)
        self.setNode2(102)
        time.sleep(0.8)
        self.setNode3(15,40)
        time.sleep(0.8)
        self.setNode1(0,35)
        time.sleep(0.8)

    def setNode1(self,angle,speed=20):
        self.servo_node1.servo_control(angle,speed)
    
    def setNode2(self,angle,speed=20):
        self.servo_node2.servo_control(angle,speed)
    
    def setNode3(self,angle,speed=20):
        self.servo_node3.servo_control(angle,speed)
    
    def setNode4(self,angle,speed=20):
        self.servo_node4.servo_control(angle,speed)
    
    def setNodeClaws(self,angle,speed=20):
        self.servo_claws.servo_control(angle,speed)



if __name__  == '__main__':
    print("ok")
    time.sleep(1)
    roboticARM = RoboticARM(True)
    
    '''time.sleep(0.8)
    
    roboticARM.setNode2(102)
    time.sleep(0.8)
    roboticARM.setNode3(15,40)
    time.sleep(1)'''
    
    time.sleep(10)
    '''time.sleep(1)
    roboticARM.setNode3(60,20)
    time.sleep(1)
    roboticARM.setNode2(120,20)
    time.sleep(1)
    roboticARM.setNodeClaws(20,15)
    time.sleep(1)
    roboticARM.setNode2(130,1)
    time.sleep(1)
    roboticARM.setNodeClaws(32,15)
    time.sleep(0.6)
    
    roboticARM.setNode2(100)
    time.sleep(1)
    roboticARM.setNode3(15)
    time.sleep(1)
    roboticARM.setNode1(125,30)
    time.sleep(3)
    roboticARM.setNode3(100)
    time.sleep(1)
    roboticARM.setNode2(80)
    time.sleep(6)
    print("end")'''
    
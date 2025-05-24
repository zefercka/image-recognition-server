from image_recognition import get_angle
import os
from robot import StatusEnum
from robot import Robot
from threading import Event
import asyncio

broker_address = os.getenv("BROKER_ADDRESS", default="192.168.1.100")
broker_port = os.getenv("BROKER_PORT", default=1883)
topic = os.getenv("COMMANDS_TOPIC", default="/devices/wb-adc/controls")


if __name__ == "__main__":
    robot = Robot(broker_address, int(broker_port), topic)
    
    while True:
        while robot.status == StatusEnum.RUNNING:
            Event().wait(0.5)
            
        angle = get_angle()
        
        print(angle)
        
        if angle == -360:
            robot.stop(10)
            break
        
        if angle > 5:
            robot.left(angle)
        elif angle < -5:
            robot.right(angle)
        else:
            robot.forward(1000)
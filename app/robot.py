from enum import StrEnum
from MQTTSender import MQTTSender
import asyncio
from threading import Event
import threading


class StatusEnum(StrEnum):
    RUNNING = "running"
    IDLE = "idle"
    

class CommandEnum(StrEnum):
    FORWARD = "forward"
    LEFT = "left"
    RIGHT = "right"
    STOP = "stop"


class Command:
    def __init__(self, command_name: CommandEnum, duration_ms: int):
        self.command_name = command_name
        self.duration_ms = duration_ms
    

class Robot:
    def __init__(self, broker_address: str, broker_port: int, base_topic: str):
        self.commands: list[Command] = []
        self.status = StatusEnum.IDLE
        self.base_topic = base_topic
        self.mqtt_client = MQTTSender(broker_address, broker_port)
        
    def left(self, angle: int):
        # Find time to move one degree
        command = Command(command_name=CommandEnum.LEFT, duration_ms=200)
        self._new_command(command)
        
    def right(self, angle: int):
        command = Command(command_name=CommandEnum.RIGHT, duration_ms=200)
        self._new_command(command)
        
    def forward(self, duration_ms: int):
        command = Command(command_name=CommandEnum.FORWARD, duration_ms=200)
        self._new_command(command)
    
    def stop(self, duration_ms: int):
        command = Command(command_name=CommandEnum.STOP, duration_ms=200)
        self._new_command(command)
        
        
    def _new_command(self, command: Command):
        self.commands.append(command)
        t = threading.Thread(target=self._run_command)
        t.start()
        Event().wait(1)
        
    def _run_command(self):
        while self.status == StatusEnum.RUNNING:
            Event().wait(0.5)
        
        print(self.status)
        
        command = self.commands[0]
        del self.commands[0]
        self.mqtt_client.publish(topic=f"{self.base_topic}/{command.command_name}", message=str(command.duration_ms))
        self.status = StatusEnum.RUNNING
        Event().wait((command.duration_ms + 1000) / 1000)
        self.status = StatusEnum.IDLE
    
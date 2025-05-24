import paho.mqtt.client as mqtt
import os

class MQTTSender:
    def __init__(self, broker_address: str, broker_port: int):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.client = mqtt.Client()
        
        self._run()
    
    def _run(self):
        try:
            self.client.connect(self.broker_address, self.broker_port)
        except Exception as err:
            print(err)
        
    def publish(self, topic: str, message: str):
        os.system(f'mosquitto_pub -h "192.168.1.100" -t "{topic}" -m "{message}"')
        # print(topic, message)
        # self.client.publish(topic, message)
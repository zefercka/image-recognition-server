import paho.mqtt.client as mqtt
import os

broker_address = os.getenv("BROKER_ADDRESS", default="127.0.0.1")
broker_port = os.getenv("BROKER_PORT", default=1883)
topic = os.getenv("COMMANDS_TOPIC", default="/devices/wb-adc/controls")

client = mqtt.Client()
client.connect(broker_address, broker_port)

while (message := input()) != "stop":
    client.publish(f"{topic}/{message.split()[0]}", message.split()[1])

client.disconnect()
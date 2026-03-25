import paho.mqtt.client as mqtt
import json
import time

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker!")

client = mqtt.Client()
client.on_connect = on_connect

well= {
        "GS_ROP": 25.0,
        "GS_RPM": 120.0,
        "GS_TQA": 2000.0,
        "GS_SWOB": 20.0,
        "GS_HKLD": 200.0,
        "GS_TFLO": 800.0,
        "GS_SPPA": 2500.0
    }
client.connect("localhost", 1883)

while True :
    client.publish("drilling/Well-01", json.dumps(well))
    time.sleep(2)

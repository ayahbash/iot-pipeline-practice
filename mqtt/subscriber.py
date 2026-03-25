import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker!")
    client.subscribe("drilling/#")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    print(f"Received from {msg.topic}:")
    print(f"  Well: {data['well_id']} | State: {data['state']} | ROP: {data['GS_ROP']} | RPM: {data['GS_RPM']}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883)
client.loop_forever()
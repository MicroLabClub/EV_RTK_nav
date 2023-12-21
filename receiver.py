import paho.mqtt.client as mqtt

username = 'sergiu.doncila'
password = 'QWEasd!@#123'
host = '9b7b323ee67e46d18f9317162c8e8841.s1.eu.hivemq.cloud'
port = 8883

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT")
    client.subscribe('microlab/automotive/#')

def on_message(client, userdata, msg):
    print(f"Received message on topic: {msg.topic}")
    message_str = msg.payload.decode('utf-8')
    print(f"Message to string: {message_str}")
    table_name = "messages_mqqt"
    if msg.topic == "microlab/automotive/device/drone/battery":
        print("Settings topic")
        print(message_str)

def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT")


def on_message2(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

# c = mqtt.Client("", True, None, mqtt.MQTTv31)

c = mqtt.Client()
c.on_connect = on_connect
c.on_message = on_message

c.tls_set()
c.username_pw_set("sergiu.doncila", "QWEasd!@#123")
c.connect("9b7b323ee67e46d18f9317162c8e8841.s1.eu.hivemq.cloud", 8883)

c.subscribe("microlab/automotive/device/atv/coordinates")
c.subscribe("microlab/automotive/device/atv/distance")

c.loop_forever()



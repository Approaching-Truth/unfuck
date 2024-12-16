import paho.mqtt.client as mqtt
import yaml

class MQTT:
    def __init__(self):
        with open("src/config.yaml", "r") as file:
            self.config = yaml.safe_load(file)
        host = self.config["mqtt"]["host"]
        port = self.config["mqtt"]["port"]
        user = self.config["mqtt"]["user"]
        password = self.config["mqtt"]["password"]
        
        self.remote_client = mqtt.Client()
        self.remote_client.username_pw_set(user, password)
        self.remote_client.connect(host, port)
        self.remote_client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

    def publish_drinking(self, data):
        self.remote_client.publish(self.config["topics"]["drinking_behaviour"], data)
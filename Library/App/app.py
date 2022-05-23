from application import Application

from func import *
from isinglethread import ISingleThread
from modules import ModuleLoader
from background import TaskLoader

from configparser import ConfigParser
import logging
import threading
from random import randint

import paho.mqtt.client as mqtt

from ngrok import Ngrok

class SploitApplication(Application):

    def __init__(self) -> None:
        self.load_config("config.ini")
        self.init_client()

        self.ngrok = Ngrok(self.config["ngrok"]["authtoken"])

        self.mloader = ModuleLoader(self.config, self.ngrok)
        self.mloader.load()

        self.tloader = TaskLoader(self.config, ngrok=self.ngrok, client=self.client)
        self.tloader.load()

        self.modules_singlethread = {}

    def run(self):
        self.client.connect(self.config['connection']['host'], self.config.getint('connection', 'port'))
        
        for t in self.tloader.get_tasks():
            self.run_task(t)
        
        self.client.loop_forever()

    def subscribe(self, *args):
        prefix = self.config['connection']['topic']
        for name, cls in self.mloader.get_modules().items():
            f = lambda *args, cls=cls: self.run_module(cls, args)
            self.client.subscribe(f"{prefix}{cls.get_topic()}/#")
            self.client.message_callback_add(f"{prefix}{cls.get_topic()}/#", f)

    def run_module(self, cls, args=[]):
        if isinstance(cls.__new__(cls), ISingleThread):
            if cls.get_module_id() not in self.modules_singlethread:
                o = cls()
                self.modules_singlethread[cls.get_module_id()] = o
            else:
                o = self.modules_singlethread[cls.get_module_id()]
        else:
            o = cls()
        t = threading.Thread(target=o.message_handler, args=[*args])
        t.name = cls.__name__ + "-" + str(randint(1000000, 9999999))
        t.start()

    def run_task(self, cls, args=[]):
        t = threading.Thread(target=cls().run, args=[*args])
        t.name = cls.__name__ + "-" + str(randint(1000000, 9999999))
        t.start()

    def load_config(self, filename):
        self.config = ConfigParser()
        if len(self.config.read(filename)) == 0:
            logging.error("Config file not found")
            exit(-1)

    def init_client(self):
        client_id = generate_client_id()
        self.client = mqtt.Client(protocol=mqtt.MQTTv311, clean_session=False, client_id=client_id)
        self.client.on_connect = self.subscribe
        if (self.config.getboolean("connection", "use_auth")):
            self.client.username_pw_set(self.config['connection']['username'], self.config['connection']['password'])

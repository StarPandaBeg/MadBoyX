from abc import ABC, abstractmethod

import logging
import json

from func import *

class BaseModule(ABC):

    modules = None
    config = None

    def message_handler(self, client, userdata, message) -> bool:
        try:
            return self._process(client, userdata, message)
        except Exception as e:
            logging.error("An error occured during message processing.")
            logging.error(f"Message: {message.topic} => {message.payload}")
            logging.exception(e)
            return False

    def _process(self, client, userdata, message) -> bool:
        prefix = self.__class__.config['connection']['topic'].rstrip("/")
        topic = remove_prefix(message.topic, prefix).strip("/").split("/")
        payload = json.loads(message.payload) if message.payload else None
        logging.debug(f"{topic} -> " + (f"payload ({len(payload)} symbols)" if payload else "no payload"))

        result = self.do(topic[1:], payload)
        topic = prefix + "/out/" + "/".join(topic)
        payload = json.dumps({"response": result}, ensure_ascii=False)

        logging.debug(f"{topic} <- " + (f"payload ({len(payload)} symbols)" if payload else "no payload"))
        client.publish(topic, payload=payload)

    @abstractmethod
    def do(self, topic, payload):
        raise NotImplementedError

    @classmethod
    def set_config(cls, config):
        cls.config = config

    @classmethod
    def set_modules(cls, modules):
        cls.modules = modules

    @staticmethod
    @abstractmethod
    def get_module_id() -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_topic() -> str:
        raise NotImplementedError
from modules.basemodule import BaseModule

class PingModule(BaseModule):

    @staticmethod
    def get_module_id() -> str:
        return "ping"

    @staticmethod
    def get_topic() -> str:
        return "ping"

    def do(self, topic, payload):
        return "pong"
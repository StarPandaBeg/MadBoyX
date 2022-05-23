from isinglethread import ISingleThread
from modules.basemodule import BaseModule
from iusengrok import IUseNgrok

from modules.fileserver.server import Server

from func import *

class FileserverModule(BaseModule, IUseNgrok, ISingleThread):

    def __init__(self) -> None:
        super().__init__()
        self.server = Server()
        self.disk = None

    @staticmethod
    def get_module_id() -> str:
        return "fileserver"

    @staticmethod
    def get_topic() -> str:
        return "files"

    def do(self, topic, payload):
        command = topic[0]

        if command == "start":
            if (payload == None or payload.get('disk') == None):
                return {"error": "No disk specified"}
            disk = payload.get('disk').upper()
            if disk not in get_drives():
                return {"error": "Disk not found"}
            self.disk = disk
            self.server.run(disk)
            return {"url": self.__class__.ngrok.forward(8000)}
        elif command == "stop":
            self.server.stop()
            self.__class__.ngrok.close(8000)
            self.disk = None
            return "OK"
        elif (command == "state"):
            return {"is_running": self.server.is_running(), "disk": self.disk, "link": self.__class__.ngrok.forward(8000) if self.ngrok.is_forward(8000) else None}
        elif (command == "available"):
            return get_drives()
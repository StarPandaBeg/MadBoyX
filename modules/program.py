import subprocess
import sys
from modules.basemodule import BaseModule

import os

class ProgramModule(BaseModule):

    @staticmethod
    def get_module_id() -> str:
        return "program"

    @staticmethod
    def get_topic() -> str:
        return "program"

    def do(self, topic, payload):
        command = topic[0] if len(topic) > 0 else None

        if (command == "restart"):
            os.startfile("restart.vbs")
            return "ok"
        elif (command == "restartinstall"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r" "requirements.txt"])
            os.startfile("restart.vbs")
            return "ok"
        elif (command == "about"):
            with open("VERSION") as f:
                version = f.read()
            # return {"version": version, "modules": list(self.__class__.modules.modules.keys())}
            return {"version": version}
        elif (command == "force_update"):
            os.remove("VERSION")
            return "ok"


    
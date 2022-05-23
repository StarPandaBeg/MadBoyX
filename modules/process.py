import subprocess
from modules.basemodule import BaseModule

import psutil

class ProcessModule(BaseModule):

    @staticmethod
    def get_module_id() -> str:
        return "process"

    @staticmethod
    def get_topic() -> str:
        return "process"

    def do(self, topic, payload):
        if len(topic) == 0:
            return "Command not specified"
        
        if topic[0] == "list":
            return self.list_processes()
        elif topic[0] == "kill":
            if not payload.get("process"):
                return "Process not specified"
            subprocess.check_call(["taskkill", "/f", "/im", payload.get("process")])
    
    def list_processes(self):
        d = []
        for proc in psutil.process_iter():
            try:
                processName = proc.name()
                processID = proc.pid
                d.append((processName, processID))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return d
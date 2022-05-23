from background.basetask import BaseTask

from time import sleep

from iuseclient import IUseClient

class PingreqTask(BaseTask, IUseClient):

    def run(self):
        while (1):
            self.client._send_pingreq()
            sleep(20)
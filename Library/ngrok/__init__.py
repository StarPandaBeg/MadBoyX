from pyngrok import conf
import ngrok.pyng as ngrok

class Ngrok:

    def __init__(self, token):
        conf.get_default().auth_token = token
        conf.get_default().region = "eu"

        self.proc = None
        self.urls = {}

        self.restart()

    def forward(self, port, conntype="http"):
        if (self.urls.get(port, None)):
            return self.urls[port].public_url
        elif (len(self.urls) >= 4):
            raise Exception("Unable to create more than 4 sessions")
        else:
            self.urls[port] = ngrok.connect(port, conntype)
            return self.urls[port].public_url

    def close(self, port):
        if (self.urls.get(port, None)):
            ngrok.disconnect(self.urls[port].public_url)
            self.urls.pop(port, None)

    def restart(self):
        if self.proc != None:
            ngrok.kill()
        self.proc = ngrok.get_ngrok_process()
        self.urls = {}

    def is_forward(self, port):
        return bool(self.urls.get(port, False))
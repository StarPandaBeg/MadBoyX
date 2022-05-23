from http.server import HTTPServer as BaseHTTPServer

from modules.fileserver.handler import HTTPHandler
from threading import Thread
from random import randint

from func import *

class HTTPServer(BaseHTTPServer):
    def __init__(self, base_path, server_address, RequestHandlerClass=HTTPHandler):
        self.base_path = base_path
        BaseHTTPServer.__init__(self, server_address, RequestHandlerClass)

class Server:
    
    def __init__(self) -> None:
        self.server_thread = None
        self.http_server = None
        
        self.disk = None

    def is_running(self):
        return self.server_thread != None

    def run(self, disk):
        if disk not in get_drives():
            return False
        if (self.server_thread):
            self.stop()
        self.disk = disk
        self.http_server = HTTPServer(f"{disk}:\\", ("", 8000))
        self.server_thread = Thread(target=self.http_server.serve_forever)
        self.server_thread.name = f"FileServer-{randint(1000000, 9999999)}"
        self.server_thread.start()
        return True

    def stop(self):
        if not self.server_thread:
            return
        self.http_server.shutdown()
        self.server_thread.__shutdown_request = True
        self.server_thread = None
        self.http_server = None
        self.disk = None
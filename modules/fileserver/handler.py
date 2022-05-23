from http.server import SimpleHTTPRequestHandler

import cgi
from io import BytesIO
import os
import shutil
import urllib
import stat

from modules.fileserver.temply import Temply

FRONT_URL = "https://xenodochial-hawking-7826a8.netlify.app"

class HTTPHandler(SimpleHTTPRequestHandler):
    
    def _send(self, code=200, content='', ctype='text/html'):
        self.send_response(code)
        self.send_header('Content-type', ctype+";charset=utf-8")
        self.end_headers()
        if content:
            self.wfile.write(content.encode("utf-8"))

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

        if ctype == "multipart/form-data":
            fields = cgi.parse_multipart(self.rfile, pdict)
            path = self.translate_path(self.path)
            if not os.path.exists(path):
                self._send(404, "Path not found")
                return
            action = fields.get("action", "")[0].decode("utf-8")
            try:
                self.do_action(action, path, fields)
            except Exception:
                self._send(500, "Unknown Error")
            else:
                self._send(200, "OK")

    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath

    def list_directory(self, path):
        directories, files = self._list_directory(path)
        if directories == None:
            self._send(403, "No permissions to list this directory")
            return

        displaypath = urllib.parse.unquote(self.path)
        tpl = Temply(base_dir="modules/fileserver/tpl")
        tpl.load_template("entry")

        for d in directories:
            tpl.set("type", "directory")
            tpl.set("img", "directory")
            tpl.set("href", d[0])
            tpl.set("name", d[0])
            tpl.set("filepath", FRONT_URL)
            tpl.setBlock("hidden", d[1])
            tpl.compile("card")

        for f in files:
            tpl.set("type", "file")
            tpl.set("img", self.get_icon_name(f[0]))
            tpl.set("href", f[0])
            tpl.set("name", f[0])
            tpl.set("filepath", FRONT_URL)
            tpl.setBlock("hidden", f[1])
            tpl.compile("card")

        tpl.load_template("main")
        tpl.set("drive", self.translate_path("/")[0])
        tpl.set("path", displaypath)
        tpl.set("filepath", FRONT_URL)
        tpl.set("content", tpl.get("card"))
        tpl.setBlock("folderup", (displaypath != "/"))
        tpl.compile("main")

        encoded = tpl.get("main").encode('utf-8', 'surrogateescape')
        f = BytesIO()
        f.write(encoded)
        f.seek(0)

        self._send()
        return f

    def _list_directory(self, path):
        directories = []
        files = []
        try:
            l = os.listdir(path)
            for f in l:
                if os.path.isdir(os.path.join(path, f)):
                    directories.append((f, self.is_hidden(os.path.join(path, f))))
                elif os.path.isfile(os.path.join(path, f)):
                    files.append((f, self.is_hidden(os.path.join(path, f))))
        except os.error:
            return (None, None)
        directories.sort()
        files.sort()
        return (directories, files)

    def get_icon_name(self, filename):
        parts = filename.split(".")
        if (len(parts) <= 1):
            return filename
        extension = parts[-1].lower()
        return extension

    def is_hidden(self, filepath):
        return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)

    def log_message(self, format, *args):
        return

    def do_action(self, action, path, fields):
        if action == "start":
            os.startfile(path)
        elif action == "archive":
            parts = path.rstrip("\\").split("\\")
            name = parts[::-1][0]
            print(name)
            shutil.make_archive(path.rstrip("\\")+"\\..\\"+name, "zip", path)
        elif action == "rename":
            if (fields.get("name", "")[0]):
                newpath = os.path.dirname(path)+"\\"+fields["name"][0].decode("utf-8")
                os.rename(path, newpath)
        elif (action == "delete"):
            if (os.path.isfile(path)):
                os.remove(path)
            elif (os.path.isdir(path)):
                shutil.rmtree(path)
        elif (action == "newfolder"):
            if (fields.get("name", "")[0]):
                newpath = path+"\\"+fields.get("name", "")[0].decode("utf-8")
                os.makedirs(newpath)
        elif (action == "upload"):
            if (fields.get("upload", "")[0] and fields.get("name", "")[0]):
                filename = fields.get("name", "")[0].decode("utf-8")
                data = fields.get("upload", "")[0]
                newpath = path+"\\"+filename
                with open(newpath, 'wb') as f:
                    f.write(data)
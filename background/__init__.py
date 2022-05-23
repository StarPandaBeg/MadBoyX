from func import *
import logging

from iusengrok import IUseNgrok
from iuseclient import IUseClient
from background.basetask import BaseTask

EXCLUDE = ["__init__.py", "basetask.py"]

class TaskLoader:

    def __init__(self, config, ngrok=None, client=None):
        self.config = config
        self.ngrok = ngrok
        self.client = client
        self.invalid = []
        self.tasks = []

    def load(self):
        self._load_filetasks()

    def get_tasks(self):
        return self.tasks

    def _load_filetasks(self):
        file_tasks = [f[:-3] for f in os.listdir(TASKS_DIR) if self._is_valid_filetask(f)]
        for filename in file_tasks:
            cls = self._get_filetask_class(filename)
            if not self._load_task(filename, cls):
                self.invalid.append(filename)

    def _load_task(self, name, cls):
        if cls == None:
            logging.warn(f"Cannot load task {name}. Invalid task.")
            return False

        o = cls.__new__(cls)
        if not isinstance(o, BaseTask):
            logging.warn(f"Cannot load task {name}. Task class should be a BaseTask subclass.")
            return False

        cls.set_config(self.config)
        if isinstance(o, IUseNgrok):
            cls.set_ngrok(self.ngrok)
        if isinstance(o, IUseClient):
            cls.set_client(self.client)
        self.tasks.append(cls)
        logging.info(f"Loaded task {name}")
        return True

    def _is_valid_filetask(self, f):
        return f.lower().endswith(".py") and (f not in EXCLUDE) and os.path.isfile(rf"{TASKS_DIR}\{f}")

    def _get_filetask_classname(self, filename):
        return filename.capitalize()+"Task"

    def _get_dirtask_classname(self, dirname):
        return dirname.capitalize()+"Task"

    def _get_filetask_class(self, filename):
        clsname = self._get_filetask_classname(filename)
        filetask = self._import_task(filename)
        return getattr(filetask, clsname, None)

    def _get_dirtask_class(self, dirname):
        clsname = self._get_dirtask_classname(dirname)
        task = self._import_task(dirname)
        return getattr(task, clsname, None)

    def _import_task(self, filename):
        return getattr(__import__(f"background.{filename}", globals()), filename)
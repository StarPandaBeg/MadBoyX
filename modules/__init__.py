from re import M
from func import *
import logging

from iusengrok import IUseNgrok
from modules.basemodule import BaseModule

EXCLUDE = ["__init__.py", "basemodule.py", "__pycache__"]

class ModuleLoader:

    def __init__(self, config, ngrok=None):
        self.config = config
        self.ngrok = ngrok
        self.invalid = []
        self.modules = {}

    def load(self):
        self._load_dirmodules()
        self._load_filemodules()

    def get_module(self, id):
        return self.modules.get(id, None)

    def get_modules(self):
        return self.modules

    def _load_filemodules(self):
        file_modules = [f[:-3] for f in os.listdir(MODULES_DIR) if self._is_valid_filemodule(f)]
        for filename in file_modules:
            cls = self._get_filemodule_class(filename)
            if not self._load_module(filename, cls, "file"):
                self.invalid.append(filename)

    def _load_dirmodules(self):
        dir_modules = [d for d in os.listdir(MODULES_DIR) if self._is_valid_dirmodule(d)]
        for dirname in dir_modules:
            cls = self._get_dirmodule_class(dirname)
            if not self._load_module(dirname, cls, "dir"):
                self.invalid.append(dirname)

    def _load_module(self, name, cls, type="file"):
        if cls == None:
            logging.warn(f"Cannot load {type} module {name}. Invalid module.")
            return False

        o = cls.__new__(cls)
        if not isinstance(o, BaseModule):
            logging.warn(f"Cannot load {type} module {name}. Module class should be a BaseModule subclass.")
            return False
        if cls.get_module_id() in self.modules.keys():
            logging.warn(f"Cannot load {type} module {name}. ID already defined.")
            return False

        cls.set_config(self.config)
        if isinstance(o, IUseNgrok):
            cls.set_ngrok(self.ngrok)
        self.modules[cls.get_module_id()] = cls
        logging.info(f"Loaded {type} module {name} #{cls.get_module_id()}")
        return True

    def _is_valid_filemodule(self, f):
        return f.lower().endswith(".py") and (f not in EXCLUDE) and os.path.isfile(rf"{MODULES_DIR}\{f}")

    def _is_valid_dirmodule(self, d):
        dirpath = rf"{MODULES_DIR}\{d}"
        if not (os.path.isdir(dirpath) and (d not in EXCLUDE)):
            return False
        if not os.path.isfile(rf"{dirpath}\__init__.py"):
            return False
        return True

    def _get_filemodule_classname(self, filename):
        return filename.capitalize()+"Module"

    def _get_dirmodule_classname(self, dirname):
        return dirname.capitalize()+"Module"

    def _get_filemodule_class(self, filename):
        clsname = self._get_filemodule_classname(filename)
        filemodule = self._import_module(filename)
        return getattr(filemodule, clsname, None)

    def _get_dirmodule_class(self, dirname):
        clsname = self._get_dirmodule_classname(dirname)
        module = self._import_module(dirname)
        return getattr(module, clsname, None)

    def _import_module(self, filename):
        return getattr(__import__(f"modules.{filename}", globals()), filename)
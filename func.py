import logging
import os
import sys
import shutil
from random import randint
import string

DEBUG_MODE = 1

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))+"\\" if DEBUG_MODE else os.path.join(os.getenv("APPDATA"), "xsploit\\")
LIB_DIR = os.path.join(ROOT_DIR, "Library\\")
MODULES_DIR = os.path.join(ROOT_DIR, "modules\\")
TASKS_DIR = os.path.join(ROOT_DIR, "background\\")

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

def init():
    configure_path()
    configure_logger()

def configure_path():
    sys.path.append(LIB_DIR)
    for dir in os.walk(LIB_DIR):
        if dir[0].find("__pycache__") != -1:
            continue
        sys.path.append(dir[0])

def configure_logger():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO, datefmt=LOG_DATE_FORMAT)

def generate_client_id():
    return f"pyxploit-{randint(100000, 999999)}"

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def get_drives():
    return ['%s' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]

def rm_if_exists(path, tree=False):
    if os.path.exists(path):
        if tree:
            shutil.rmtree(path)
        else:
            os.remove(path)

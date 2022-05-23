from abc import ABC, abstractmethod

class BaseTask(ABC):

    config = None

    @classmethod
    def set_config(cls, config):
        cls.config = config

    @abstractmethod
    def run(self):
        pass
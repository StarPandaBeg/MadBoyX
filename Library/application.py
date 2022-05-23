from abc import ABC, abstractmethod

class Application(ABC):
    
    @abstractmethod
    def run(self):
        pass
from abc import ABC, abstractmethod


class ITask(ABC):
    @abstractmethod
    def execute(self):
        pass

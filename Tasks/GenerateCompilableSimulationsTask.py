import BenchmarkConfig
from Tasks.ITask import ITask


class GenerateCompilableSimulationsITask(ITask):
    config: BenchmarkConfig

    def __init__(self, config: BenchmarkConfig):
        self.config = config

    def execute(self):
        pass
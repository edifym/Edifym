import MainConfig
from BenchmarkConfig import Benchmark
from Tasks.ITask import ITask
import subprocess
import os
from slinkie import Slinkie


class CompileSingleSimulationITask(ITask):
    main_config: MainConfig
    benchmark: Benchmark

    def __init__(self, main_config: MainConfig, benchmark: Benchmark):
        self.main_config = main_config
        self.benchmark = benchmark

    def execute(self):
        new_env = os.environ.copy()
        new_env['M5_DIR'] = self.main_config.gem5_path
        new_env['LIBRARY_UNDER_TEST'] = self.main_config.library_name
        new_env['TASK_SIZE'] = len(self.benchmark.tasks)
        new_env['TASKS'] = '{' + ', '.join(Slinkie(self.benchmark.tasks).map(lambda it: f"\"{it.name}\"")) + '}'
        print f"{new_env['TASKS']}"

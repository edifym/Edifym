import MainConfig
from BenchmarkConfig import Benchmark
from Tasks.ITask import ITask
import subprocess
import os
import sys
from slinkie import Slinkie


class CompileSingleSimulationTask(ITask):
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
        new_env['TASKS'] = '{' + Slinkie(self.benchmark.tasks).map(lambda it: f"\"{it.name}\"").join(', ') + '}'
        try:
            proc = subprocess.Popen('cmake .', env=new_env)
            output, error = proc.communicate()
            if output:
                print(f"cmake output> {proc.returncode} {output}")
            if error:
                print(f"cmake error> {proc.returncode} {error.strip()}")
        except OSError as e:
            print(f"OSError> {e.errno} {e.strerror} {e.filename}")
        except:
            print(f"Error> {sys.exc_info()[0]}")

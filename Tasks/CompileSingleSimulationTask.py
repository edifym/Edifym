import MainConfig
from BenchmarkConfig import Benchmark
from Tasks.ITask import ITask
import subprocess
import os
import sys
from slinkie import Slinkie
from typing import List, Dict


class CompileSingleSimulationTask(ITask):
    main_config: MainConfig
    benchmark: Benchmark

    def __init__(self, main_config: MainConfig, benchmark: Benchmark):
        self.main_config = main_config
        self.benchmark = benchmark

    def run_command(self, command: List[str], new_env: Dict[str, str]):
            proc = subprocess.Popen(command, cwd='./EdifymRunner', env=new_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = proc.communicate()
            if output:
                print(f"cmake output> {proc.returncode} {output}")
            if error:
                print(f"cmake error> {proc.returncode} {error.strip()}")

    def execute(self):
        new_env = os.environ.copy()
        new_env['M5_DIR'] = self.main_config.gem5_path
        new_env['LIBRARY_UNDER_TEST'] = self.main_config.library_name
        new_env['TASK_SIZE'] = str(len(self.benchmark.tasks))
        new_env['TASKS'] = '{' + Slinkie(self.benchmark.tasks).map(lambda it: f"\"{it.name}\"").join(', ') + '}'
        try:
            self.run_command(['cmake', '.'], new_env)
            self.run_command(['make'], new_env)
        except OSError as e:
            print(f"OSError> {e.errno} {e.strerror} {e.filename}")
        except TypeError as e:
            print(f"TypeError> {e}")
        except:
            print(f"Error> {sys.exc_info()[0]}")

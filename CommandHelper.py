import subprocess
import os
from typing import List, Dict
import MainConfig
from BenchmarkConfig import Benchmark
from slinkie import Slinkie


class CommandHelper:

    @staticmethod
    def run_command(command: List[str], new_env: Dict[str, str], cwd: str = './EdifymRunner'):
            proc = subprocess.Popen(command, cwd=cwd, env=new_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f'executing {proc.args}')
            output, error = proc.communicate()
            if output:
                print(f'{command[0]} output> {proc.returncode} {output}')
            if error:
                print(f'{command[0]} error> {proc.returncode} {error.strip()}')

    @staticmethod
    def create_environment_from_config(config: MainConfig, benchmark: Benchmark) -> Dict[str, str]:
        new_env = os.environ.copy()
        new_env['M5_DIR'] = config.m5_path
        new_env['LIBRARY_UNDER_TEST'] = config.library_name
        new_env['TASK_SIZE'] = str(len(benchmark.tasks))
        new_env['TASKS'] = '{' + Slinkie(benchmark.tasks).map(lambda it: f'"{it.name}"').join(', ') + '}'
        return new_env

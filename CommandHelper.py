import subprocess
import os
from typing import List, Dict
import MainConfig
from BenchmarkConfig import Benchmark
from slinkie import Slinkie


class CommandHelper:

    @staticmethod
    def preexec_function():
        os.setpgrp()

    @staticmethod
    def run_command(command: List[str], new_env: Dict[str, str], show_output: bool = True, show_error: bool = True, cwd: str = './EdifymRunner'):
            proc = subprocess.Popen(command, cwd=cwd, env=new_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=CommandHelper.preexec_function)
            if show_output:
                args = ' '.join(proc.args)
                print('executing %s' % args)

            output, error = proc.communicate()

            if show_output and output:
                print('%s output> %s %s' % (command[0], proc.returncode, output))
            if show_error and error:
                print('%s error> %s %s' % (command[0], proc.returncode, error.strip()))

    @staticmethod
    def run_command_output(command: List[str], new_env: Dict[str, str], cwd: str = './EdifymRunner') -> str:
            proc = subprocess.Popen(command, cwd=cwd, env=new_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=CommandHelper.preexec_function)

            output, error = proc.communicate()

            return output

    @staticmethod
    def create_environment_from_config(config: MainConfig, benchmark: Benchmark) -> Dict[str, str]:
        new_env = os.environ.copy()
        new_env['M5_DIR'] = config.m5_path
        new_env['LIBRARY_UNDER_TEST'] = config.library_name
        new_env['TASK_SIZE'] = str(len(benchmark.tasks))
        new_env['TASKS'] = '{' + Slinkie(benchmark.tasks).map(lambda it: it.name).join(', ') + '}'
        return new_env

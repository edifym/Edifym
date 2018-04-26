import MainConfig
from BenchmarkConfig import Benchmark
from Tasks.ITask import ITask
import subprocess
import os
import sys
import jsonpickle
import itertools
from slinkie import Slinkie
from typing import List, Dict


class CompileSingleSimulationTask(ITask):
    main_config: MainConfig
    benchmark: Benchmark
    config_number: int

    def __init__(self, main_config: MainConfig, benchmark: Benchmark, config_number: int):
        self.main_config = main_config
        self.benchmark = benchmark
        self.config_number = config_number

    def run_command(self, command: List[str], new_env: Dict[str, str]):
            proc = subprocess.Popen(command, cwd='./EdifymRunner', env=new_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f'executing {proc.args}')
            output, error = proc.communicate()
            if output:
                print(f'{command[0]} output> {proc.returncode} {output}')
            if error:
                print(f'{command[0]} error> {proc.returncode} {error.strip()}')

    def produce_combinations(self):
        for L in range(1, len(self.benchmark.tasks)+1):
            for subset in itertools.combinations(self.benchmark.tasks, L):
                print(subset)

    def object_as_json_to_file(self, filepath: str, object):
        if(jsonpickle.load_backend('simplejson')):
            jsonpickle.set_preferred_backend('simplejson')
            jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=4)
        else:
            print('Couldn\'t load simplejson')
        with open(filepath, 'w') as outfile:
            json_output = jsonpickle.encode(object, unpicklable=False)
            outfile.write(json_output)


    def execute(self):
        new_env = os.environ.copy()
        new_env['M5_DIR'] = self.main_config.m5_path
        new_env['LIBRARY_UNDER_TEST'] = self.main_config.library_name
        new_env['TASK_SIZE'] = str(len(self.benchmark.tasks))
        new_env['TASKS'] = '{' + Slinkie(self.benchmark.tasks).map(lambda it: f'"{it.name}"').join(', ') + '}'
        try:
            self.run_command(['cmake', '.'], new_env)
            self.run_command(['make'], new_env)
            self.run_command(['mkdir', '-p', f'../out/{self.config_number}'], new_env)
            self.run_command(['cp', 'EdifymRunner', f'../out/{self.config_number}'], new_env)

            self.object_as_json_to_file(f'out/{self.config_number}/benchmark.json', self.benchmark)
            self.object_as_json_to_file(f'out/{self.config_number}/config.json', self.main_config)
        except OSError as e:
            print(f'OSError> {e.errno} {e.strerror} {e.filename}')
        except TypeError as e:
            print(f'TypeError> {e}')
        except AttributeError as e:
            print(f'AttributeError> {e}')
        except AssertionError as e:
            print(f'AssertionError> {e}')
        except:
            print(f'Error> {sys.exc_info()[0]}')

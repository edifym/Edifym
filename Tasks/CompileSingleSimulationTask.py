from JsonHelper import JsonHelper
from CommandHelper import CommandHelper
import MainConfig
from BenchmarkConfig import Benchmark
from Tasks.ITask import ITask
import sys


class CompileSingleSimulationTask(ITask):
    main_config: MainConfig
    benchmark: Benchmark
    config_number: int

    def __init__(self, main_config: MainConfig, benchmark: Benchmark, config_number: int):
        self.main_config = main_config
        self.benchmark = benchmark
        self.config_number = config_number

    def execute(self):
        print(f'Starting CompileSingleSimulationTask {self.config_number}')
        try:
            new_env = CommandHelper.create_environment_from_config(self.main_config, self.benchmark)
            CommandHelper.run_command(['mkdir', '-p', f'./builds/{self.config_number}'], new_env, self.main_config.show_command_output)

            CommandHelper.run_command(['cmake', '../../'], new_env, self.main_config.show_command_output, f'./EdifymRunner/builds/{self.config_number}')
            CommandHelper.run_command(['make'], new_env, self.main_config.show_command_output, f'./EdifymRunner/builds/{self.config_number}')
            CommandHelper.run_command(['mkdir', '-p', f'../../../out/{self.config_number}'], new_env, self.main_config.show_command_output, f'./EdifymRunner/builds/{self.config_number}')
            CommandHelper.run_command(['cp', 'EdifymRunner', f'../../../out/{self.config_number}'], new_env, self.main_config.show_command_output, f'./EdifymRunner/builds/{self.config_number}')

            JsonHelper.object_as_json_to_file(f'out/{self.config_number}/benchmark.json', self.benchmark)
            JsonHelper.object_as_json_to_file(f'out/{self.config_number}/config.json', self.main_config)
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

        print(f'CompileSingleSimulationTask done {self.config_number}')

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
        #print(f'Starting CompileSingleSimulationTask {self.config_number}')
        try:
            new_env = CommandHelper.create_environment_from_config(self.main_config, self.benchmark)

            CommandHelper.run_command(['mkdir', '-p', f'{self.main_config.build_dir}/{self.config_number}'], new_env, self.main_config.show_command_output)
            CommandHelper.run_command(['cmake', f'{self.main_config.src_dir}'], new_env, self.main_config.show_command_output, f'{self.main_config.build_dir}/{self.config_number}')
            CommandHelper.run_command(['make'], new_env, self.main_config.show_command_output, f'{self.main_config.build_dir}/{self.config_number}')
            CommandHelper.run_command(['mkdir', '-p', f'{self.main_config.out_dir}/{self.config_number}'], new_env, self.main_config.show_command_output)
            CommandHelper.run_command(['mv', 'EdifymRunner', f'{self.main_config.out_dir}/{self.config_number}'], new_env, self.main_config.show_command_output, f'{self.main_config.build_dir}/{self.config_number}')
            CommandHelper.run_command(['rm', '-rf', f'{self.main_config.build_dir}/{self.config_number}'], new_env, self.main_config.show_command_output)

            JsonHelper.object_as_json_to_file(f'{self.main_config.out_dir}/{self.config_number}/benchmark.json', self.benchmark)
            JsonHelper.object_as_json_to_file(f'{self.main_config.out_dir}/{self.config_number}/config.json', self.main_config)
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

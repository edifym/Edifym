from CommandHelper import CommandHelper
import MainConfig
from BenchmarkConfig import Benchmark
from Tasks.ITask import ITask
import sys
import jsonpickle


class CompileSingleSimulationTask(ITask):
    main_config: MainConfig
    benchmark: Benchmark
    config_number: int

    def __init__(self, main_config: MainConfig, benchmark: Benchmark, config_number: int):
        self.main_config = main_config
        self.benchmark = benchmark
        self.config_number = config_number

    @staticmethod
    def object_as_json_to_file(filepath: str, object_to_store):
        if jsonpickle.load_backend('simplejson'):
            jsonpickle.set_preferred_backend('simplejson')
            jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=4)
        else:
            print('Couldn\'t load simplejson')
        with open(filepath, 'w') as outfile:
            json_output = jsonpickle.encode(object_to_store, unpicklable=False)
            outfile.write(json_output)

    def execute(self):
        try:
            new_env = CommandHelper.create_environment_from_config(self.main_config, self.benchmark)
            CommandHelper.run_command(['cmake', '.'], new_env)
            CommandHelper.run_command(['make'], new_env)
            CommandHelper.run_command(['mkdir', '-p', f'../out/{self.config_number}'], new_env)
            CommandHelper.run_command(['cp', 'EdifymRunner', f'../out/{self.config_number}'], new_env)

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

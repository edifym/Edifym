import CommandHelper
import MainConfig
from Tasks.ITask import ITask
import sys


class RunSingleSimulationTask(ITask):
    main_config: MainConfig
    run_number: int

    def __init__(self, main_config: MainConfig, run_number: int):
        self.main_config = main_config
        self.run_number = run_number

    def execute(self):
        try:
            CommandHelper.run_command([self.main_config.gem5_executable_path, self.main_config.gem5_se_script_path,
                                       '--cpu-type', 'DerivO3CPU', '--caches', '--num-l2caches=0', '--num-l3caches=0',
                                       '-n', '2', '-c',
                                       f'"../out/{self.run_number}/EdifymRunner;../out/{self.run_number}/EdifymRunner"'], {})
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

from CommandHelper import CommandHelper
import MainConfig
from JsonHelper import JsonHelper
from Tasks.ITask import ITask
import sys
from typing import List


class RunSingleSimulationTask(ITask):
    main_config: MainConfig
    num_cpus: int
    run_numbers: List[int]
    id: int

    def __init__(self, main_config: MainConfig, num_cpus: int, run_numbers: List[int], id: int):
        self.main_config = main_config
        self.num_cpus = num_cpus
        self.run_numbers = run_numbers
        self.id = id

    def execute(self):
        #print(f'Starting RunSingleSimulationTask {self.id}')
        try:
            if len(self.run_numbers) != self.num_cpus:
                raise AssertionError(f'length of run_numbers ({len(self.run_numbers)}) '
                                     f'is not equal to num_cpus ({self.num_cpus})')

            workload = ' '.join(map(lambda num: f'{self.main_config.out_dir}/{num}/EdifymRunner', self.run_numbers))

            CommandHelper.run_command(['mkdir', '-p', f'{self.main_config.out_dir}/run_{self.id}'], {}, self.main_config.show_command_output)
            CommandHelper.run_command([self.main_config.gem5_executable_path, self.main_config.gem5_se_script_path,
                                       '--cpu-freq', '10MHz', '--disable-l2', '1', '--num-cores', str(self.num_cpus), workload], {}, self.main_config.show_command_output, f'{self.main_config.out_dir}/run_{self.id}')
            CommandHelper.run_command(['mkdir', '-p', f'{self.main_config.stats_dir}/run_{self.id}'], {}, self.main_config.show_command_output)
            CommandHelper.run_command(['mv', f'm5out/stats.txt', f'{self.main_config.stats_dir}/run_{self.id}'], {}, self.main_config.show_command_output, f'{self.main_config.out_dir}/run_{self.id}')
            CommandHelper.run_command(['rm', f'-rf', f'{self.main_config.out_dir}/run_{self.id}'], {}, self.main_config.show_command_output)

            JsonHelper.object_as_json_to_file(f'{self.main_config.stats_dir}/run_{self.id}/run_numbers.json', self.run_numbers)
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
        print(f'RunSingleSimulationTask done {self.id}')

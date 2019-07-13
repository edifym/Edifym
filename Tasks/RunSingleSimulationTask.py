from CommandHelper import CommandHelper
import MainConfig
from JsonHelper import JsonHelper
from Tasks.ITask import ITask
import sys
from typing import List


class RunSingleSimulationTask(ITask):
    main_config: MainConfig
    num_cpus: int
    workloads: List[str]
    run_id: int

    def __init__(self, main_config: MainConfig, num_cpus: int, workloads: List[str], run_id: int):
        self.main_config = main_config
        self.num_cpus = num_cpus
        self.workloads = workloads
        self.run_id = run_id

    def execute(self):
        print(f'Starting RunSingleSimulationTask {self.run_id} {self.workloads}')

        try:
            if len(self.workloads) != self.num_cpus:
                raise AssertionError(f'length of workloads ({len(self.workloads)}) '
                                     f'is not equal to num_cpus ({self.num_cpus})')

            gem5_args: List[str] = [self.main_config.gem5_executable_path, self.main_config.gem5_se_script_path,
                                    '--cpu-freq', self.main_config.cpu_freq, '--disable-l2', '1', '--num-cores',
                                    str(self.num_cpus)]
            gem5_args.extend(self.workloads)

            CommandHelper.run_command(['mkdir', '-p', f'{self.main_config.out_dir}/run_{self.run_id}'], {}, self.main_config.show_command_output, self.main_config.show_command_error)
            CommandHelper.run_command(gem5_args, {}, self.main_config.show_command_output, self.main_config.show_command_error, f'{self.main_config.out_dir}/run_{self.run_id}')
            CommandHelper.run_command(['mkdir', '-p', f'{self.main_config.stats_dir}/run_{self.run_id}'], {}, self.main_config.show_command_output, self.main_config.show_command_error)
            CommandHelper.run_command(['zstd', '-1', '--rm', '-f', f'stats.txt'], {}, self.main_config.show_command_output, self.main_config.show_command_error, f'{self.main_config.out_dir}/run_{self.run_id}/m5out')
            CommandHelper.run_command(['mv', f'm5out/stats.txt.zst', f'{self.main_config.stats_dir}/run_{self.run_id}'], {}, self.main_config.show_command_output, self.main_config.show_command_error, f'{self.main_config.out_dir}/run_{self.run_id}')
            CommandHelper.run_command(['rm', f'-rf', f'{self.main_config.out_dir}/run_{self.run_id}'], {}, self.main_config.show_command_output, self.main_config.show_command_error)

            JsonHelper.object_as_json_to_file(f'{self.main_config.stats_dir}/run_{self.run_id}/workloads.json', self.workloads)
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

        print(f'RunSingleSimulationTask done {self.run_id}')

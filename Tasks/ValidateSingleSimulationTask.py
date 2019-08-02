from CommandHelper import CommandHelper
import MainConfig
from JsonHelper import JsonHelper
from Tasks.ITask import ITask
import sys
from typing import List


class ValidateSingleSimulationTask(ITask):
    main_config: MainConfig
    num_cpus: int
    workloads: List[str]
    run_id: int
    rank: int
    find_runs_with_this_time: int

    def __init__(self, main_config: MainConfig, workloads: List[str], rank: int, run_id: int, num_cpus: int, find_runs_with_this_time: int):
        self.main_config = main_config
        self.num_cpus = num_cpus
        self.workloads = workloads
        self.run_id = run_id
        self.rank = rank
        self.find_runs_with_this_time = find_runs_with_this_time

    def execute(self):
        try:
            if len(self.workloads) != self.num_cpus:
                raise AssertionError(f'length of workloads ({len(self.workloads)}) '
                                     f'is not equal to num_cpus ({self.num_cpus})')

            gem5_args: List[str] = [self.main_config.gem5_executable_path, self.main_config.gem5_se_script_path,
                                    '--cpu-freq', self.main_config.cpu_freq, '--disable-l2', '1', '--num-cores',
                                    str(self.num_cpus)]
            gem5_args.extend(self.workloads)

            CommandHelper.run_command(['mkdir', '-p', f'{self.main_config.out_dir}/run_{self.rank}_{self.run_id}'], self.main_config.show_command_output, self.main_config.show_command_error)
            CommandHelper.run_command(gem5_args, self.main_config.show_command_output, self.main_config.show_command_error, f'{self.main_config.out_dir}/run_{self.rank}_{self.run_id}')
            stats = CommandHelper.run_command_output(['awk', '/sim_sec/ {print $2}', f'stats.txt'], f'{self.main_config.out_dir}/run_{self.rank}_{self.run_id}/m5out').splitlines()
            CommandHelper.run_command(['rm', f'-rf', f'{self.main_config.out_dir}/run_{self.rank}_{self.run_id}'], self.main_config.show_command_output, self.main_config.show_command_error)

            if len(stats) == 27:
                total_time_for_tasks = 0
                for i in range(26):
                    if i % 2 != 0:
                        total_time_for_tasks += int(stats[i][2:]) - int(stats[i - 1][2:])

                if total_time_for_tasks > self.find_runs_with_this_time:
                    print(f'node {self.rank} found higher simulation time {total_time_for_tasks} for workload {self.workloads}')

                CommandHelper.run_command(['mkdir', '-p', f'{self.main_config.stats_dir}/run_{self.rank}_{self.run_id}'], self.main_config.show_command_output, self.main_config.show_command_error)
                JsonHelper.object_as_json_to_file(f'{self.main_config.stats_dir}/run_{self.rank}_{self.run_id}/workloads.json', [self.workloads, total_time_for_tasks])
            else:
                print(f'Node {self.rank} wrong stats length {len(stats)}')
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

        print(f'Node {self.rank} ValidateSingleSimulationTask done {self.run_id:,}')

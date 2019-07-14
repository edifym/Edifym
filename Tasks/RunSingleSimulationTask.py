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
        print('Starting RunSingleSimulationTask %s %s' % (self.run_id, self.workloads))

        try:
            if len(self.workloads) != self.num_cpus:
                raise AssertionError('length of workloads (%s) is not equal to num_cpus (%s)' % (len(self.workloads), self.num_cpus))

            gem5_args: List[str] = [self.main_config.gem5_executable_path, self.main_config.gem5_se_script_path,
                                    '--cpu-freq', self.main_config.cpu_freq, '--disable-l2', '1', '--num-cores',
                                    str(self.num_cpus)]
            gem5_args.extend(self.workloads)

            CommandHelper.run_command(['mkdir', '-p', '%s/run_%s' % (self.main_config.out_dir, self.run_id)], {}, self.main_config.show_command_output, self.main_config.show_command_error)
            CommandHelper.run_command(gem5_args, {}, self.main_config.show_command_output, self.main_config.show_command_error, '%s/run_%s' % (self.main_config.out_dir, self.run_id))
            CommandHelper.run_command(['mkdir', '-p', '%s/run_%s' % (self.main_config.stats_dir, self.run_id)], {}, self.main_config.show_command_output, self.main_config.show_command_error)
            CommandHelper.run_command([self.main_config.zstd, '-1', '--rm', '-f', 'stats.txt'], {}, self.main_config.show_command_output, self.main_config.show_command_error, '%s/run_%s/m5out' % (self.main_config.out_dir, self.run_id))
            CommandHelper.run_command(['mv', 'm5out/stats.txt.zst', '%s/run_%s' % (self.main_config.stats_dir, self.run_id)], {}, self.main_config.show_command_output, self.main_config.show_command_error, '%s/run_%s' % (self.main_config.out_dir, self.run_id))
            CommandHelper.run_command(['rm', '-rf', '%s/run_%s' % (self.main_config.out_dir, self.run_id)], {}, self.main_config.show_command_output, self.main_config.show_command_error)

            JsonHelper.object_as_json_to_file('%s/run_%s/workloads.json' % (self.main_config.stats_dir, self.run_id), self.workloads)
        except OSError as e:
            print('OSError> %s %s %s' % (e, e.strerror, e.filename))
        except TypeError as e:
            print('TypeError> %s' % e)
        except AttributeError as e:
            print('AttributeError> %s' % e)
        except AssertionError as e:
            print('AssertionError> %s' % e)
        except:
            print('Error> %s' % sys.exc_info()[0])

        print('RunSingleSimulationTask done %s' % self.run_id)

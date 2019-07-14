import itertools
from multiprocessing import Queue, Value

import MainConfig
from Tasks.ITask import ITask
from typing import List, Iterator, Tuple

from BenchmarkConfig import Benchmark, Task

from Tasks.RunSingleSimulationTask import RunSingleSimulationTask


def anydup(thelist):
    seen = set()
    for x in thelist:
        if x in seen: return True
        seen.add(x)
    return False


class GenerateThreadsSimulationsTask(ITask):
    main_config: MainConfig
    q: Queue
    shm_quit: Value
    benchmark: Benchmark

    def __init__(self, main_config: MainConfig, benchmark: Benchmark, q: Queue, shm_quit: Value):
        self.main_config = main_config
        self.q = q
        self.shm_quit = shm_quit
        self.benchmark = benchmark

    def produce_task_permutations(self) -> Iterator[List[Task]]:
        print('produce_task_permutations')
        for L in range(0, len(self.benchmark.tasks) + 1):
            count = 0
            print(f'L: {L}')
            for sub_benchmark in itertools.permutations(self.benchmark.tasks, L):
                if count > 1_000 or self.shm_quit.value:
                    print(f'breaking at {count}')
                    break

                count += 1

                yield sub_benchmark

    def produce_tasks_per_core_permutations(self, tasks: Iterator[List[Task]]) -> Iterator[List[List[Task]]]:
        for workloads in itertools.permutations(tasks, self.main_config.num_cpus):
            if self.shm_quit.value:
                break

            yield workloads

    def execute(self):
        print(f'Starting GenerateThreadsSimulationsTask {len(self.benchmark.tasks)}')

        run_id = 1
        count_checked = 0
        tasks = self.produce_task_permutations()
        task_per_core = self.produce_tasks_per_core_permutations(tasks)
        for task_permutation in task_per_core:
            count_checked += 1

            if count_checked % 1_000_000 == 0:
                print(f'Checked {count_checked} tasks, added {run_id - 1} tasks')

            if sum(map(len, task_permutation)) != len(self.benchmark.tasks):
                continue

            flat_list = [item for sublist in task_permutation for item in sublist]

            if anydup(flat_list):
                continue

            run_args: List[str] = []
            for tasks_for_one_core in task_permutation:
                args = f"{self.main_config.executable} {len(tasks_for_one_core)} "

                for task in tasks_for_one_core:
                    args += task.name + ";"

                args = args[:-1]
                args += " "

                for task in tasks_for_one_core:
                    if task.values:
                        for value in task.values:
                            args += str(value.values[0]) + ";"

                        args = args[:-1]
                        args += " "
                    else:
                        args += "0 "

                run_args.append(args)

            #print(f'Running {run_args} {run_id}')
            new_task = RunSingleSimulationTask(self.main_config, self.main_config.num_cpus, run_args, run_id)
            self.q.put(new_task)
            run_id += 1

            if self.shm_quit.value:
                break

        print('GenerateThreadsSimulationsTask done')

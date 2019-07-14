import itertools
from multiprocessing import Queue, Value

import MainConfig
from Tasks.ITask import ITask
from typing import List, Iterator, Tuple

from BenchmarkConfig import Benchmark, Task

from Tasks.RunSingleSimulationTask import RunSingleSimulationTask


class Workload:
    tasks: List[Task]
    values: List[Tuple[int]]

    def __init__(self, tasks: List[Task], values: List[Tuple[int]]):
        self.tasks = tasks
        self.values = values


class GenerateValueSimulationsTask(ITask):
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
                #print(f'sub_benchmark: {sub_benchmark}')

                if count > 10 or self.shm_quit.value:
                    print(f'breaking at {count}')
                    break

                count += 1

                yield sub_benchmark

    def produce_workload_permutations(self, tasks: Iterator[List[Task]]) -> Iterator[List[Workload]]:
        for workloads in itertools.permutations(tasks, self.main_config.num_cpus):
            print(f'workloads: {workloads}')
            ret: List[Workload] = []
            for workload in workloads:
                #print(f'workload: {workload}')
                if workload:
                    tempvals = []
                    for task in workload:
                        task_values = []
                        for val in task.values:
                            task_values.append(val.values)
                        if task_values:
                            tempvals.extend(task_values)
                        else:
                            tempvals.append([0])
                    if tempvals:
                        values = list(itertools.product(*tempvals))
                        #print(f'values: {values} {tempvals} ')
                        ret.append(Workload(workload, values))
                    else:
                        ret.append(Workload([], []))
                else:
                    ret.append(Workload([], []))

            if self.shm_quit.value:
                break

            yield ret

    def execute(self):
        print(f'Starting GenerateValueSimulationsTask {len(self.benchmark.tasks)}')

        run_id = 1
        count = 0
        for task_permutation in self.produce_workload_permutations(self.produce_task_permutations()):
            x = []
            for i in range(len(task_permutation)):
                task_permutation[i].values

            run_args: List[str] = []
            for workload in task_permutation:
                args = f"{self.main_config.executable} {len(workload.tasks)} "

                for task in workload.tasks:
                    args += task.name + ";"

                args = args[:-1]
                args += " "

                for value_tuple in workload.values:
                    for value in value_tuple:
                        args += str(value) + ";"

                    args = args[:-1]
                    args += " "

                run_args.append(args)

            print(f'Running {run_args} {run_id}')
            new_task = RunSingleSimulationTask(self.main_config, self.main_config.num_cpus, run_args, run_id)
            self.q.put(new_task)
            run_id += 1
            count += 1

            if count >= 10 or self.shm_quit.value:
                break

        print('GenerateValueSimulationsTask done')

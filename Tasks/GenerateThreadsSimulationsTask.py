import itertools
import datetime

import MainConfig
from Tasks.ITask import ITask
from typing import List, Iterator

from BenchmarkConfig import Benchmark, Task
from Tasks.RunSingleSimulationTask import RunSingleSimulationTask
from Tasks.ValidateSingleSimulationTask import ValidateSingleSimulationTask


class GenerateThreadsSimulationsTask(ITask):
    main_config: MainConfig
    benchmark: Benchmark
    skip: int
    rank: int

    def __init__(self, main_config: MainConfig, benchmark: Benchmark, rank: int, skip: int):
        self.main_config = main_config
        self.benchmark = benchmark
        self.skip = skip
        self.rank = rank

    def produce_task_permutations(self, tasks: List[Task]) -> Iterator[List[Task]]:
        for workloads in itertools.islice(itertools.permutations(tasks, len(tasks)), self.rank * self.skip, (self.rank + 1) * self.skip):
            yield workloads

    def get_run_args(self, tasks: List[Task]) -> str:
        args = f"{self.main_config.executable} {len(tasks)} "

        for task in tasks:
            args += task.name + ";"

        args = args[:-1]
        args += " "

        for task in tasks:
            if task.values:
                for value in task.values:
                    args += str(value.values[0]) + ";"

                args = args[:-1]
                args += " "
            else:
                args += "0 "

        return args

    def execute(self):
        start = datetime.datetime.now()
        print(f'node {self.rank} starting GenerateThreadsSimulationsTask {len(self.benchmark.tasks)} {start}')

        run_id = 1
        for task_permutation in self.produce_task_permutations(self.benchmark.tasks):
            for x in range(len(self.benchmark.tasks) + 1):
                core_one = task_permutation[:x]
                core_two = task_permutation[x:]
                run_args: List[str] = [self.get_run_args(core_one), self.get_run_args(core_two)]

                ValidateSingleSimulationTask(self.main_config, run_args, self.rank, run_id, self.main_config.num_cpus, 6000).execute()

                run_id += 1

        end = datetime.datetime.now()
        print(f'node {self.rank} GenerateThreadsSimulationsTask done {end - start}')

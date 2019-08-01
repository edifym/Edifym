import itertools
import datetime

import MainConfig
from Tasks.ITask import ITask
from typing import List, Iterator

from BenchmarkConfig import Benchmark, Task
from Tasks.RunSingleSimulationTask import RunSingleSimulationTask


class GenerateThreadsAndValuesSimulationsTask(ITask):
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

    def get_run_args(self, tasks: List[Task], values: List[int]) -> str:
        args = f"{self.main_config.executable} {len(tasks)} "

        total_values_expected = sum([len(t.values) for t in tasks])

        if len(values) != total_values_expected:
            print(f'Total values {len(values)} not equal to {total_values_expected}')
            raise Exception

        for task in tasks:
            args += task.name + ";"

        args = args[:-1]
        args += " "

        values_had = 0
        for task in tasks:
            if len(task.values) == 0:
                args += "0"
            else:
                useful_values = values[values_had:values_had + len(task.values)]
                for val in useful_values:
                    args += f'{val};'
                    values_had += 1
                args = args[:-1]

            args += " "

        return args

    def get_workloads(self, tasks_core_one: List[Task], tasks_core_two: List[Task]) -> Iterator[List[str]]:
        if any(tasks_core_one) and any(tasks_core_two):
            for values_c1 in itertools.product(*[v.values for x in tasks_core_one for v in x.values]):
                for values_c2 in itertools.product(*[v.values for x in tasks_core_two for v in x.values]):
                    yield [self.get_run_args(tasks_core_one, values_c1), self.get_run_args(tasks_core_two, values_c2)]

        elif any(tasks_core_one):
            for values_c1 in itertools.product(*[v.values for x in tasks_core_one for v in x.values]):
                yield [self.get_run_args(tasks_core_one, values_c1), self.get_run_args([], [])]

        elif any(tasks_core_two):
            for values_c2 in itertools.product(*[v.values for x in tasks_core_two for v in x.values]):
                yield [self.get_run_args([], []), self.get_run_args(tasks_core_two, values_c2)]

    def execute(self):
        start = datetime.datetime.now()
        print(f'node {self.rank} starting GenerateThreadsAndValuesSimulationsTask {len(self.benchmark.tasks)} {start}')

        run_id = 1
        for task_permutation in self.produce_task_permutations(self.benchmark.tasks):
            for x in range(len(self.benchmark.tasks) + 1):
                core_one = task_permutation[:x]
                core_two = task_permutation[x:]
                for run_args in self.get_workloads(core_one, core_two):
                    RunSingleSimulationTask(self.main_config, run_args, self.rank, run_id, self.main_config.num_cpus).execute()
                    run_id += 1

        end = datetime.datetime.now()
        print(f'node {self.rank} GenerateThreadsAndValuesSimulationsTask done {end - start}')

import itertools
import datetime

import MainConfig
from Tasks.ITask import ITask
from typing import List, Iterator

from BenchmarkConfig import Task
from Tasks.RunSingleSimulationTask import RunSingleSimulationTask


class GenerateWcetPerTaskSimulationsTask(ITask):
    main_config: MainConfig
    tasks: List[Task]
    rank: int

    def __init__(self, main_config: MainConfig, tasks: List[Task], rank: int):
        self.main_config = main_config
        self.tasks = tasks
        self.rank = rank

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

    def get_workloads(self, task: Task) -> Iterator[str]:
        for values in itertools.product(*[x.values for x in task.values]):
            yield self.get_run_args([task], values)

    def execute(self):
        start = datetime.datetime.now()
        print(f'node {self.rank} starting GenerateWcetPerTaskSimulationsTask {len(self.tasks)} {start}')

        run_id = 1
        for task in self.tasks:
            for run_args in self.get_workloads(task):
                RunSingleSimulationTask(self.main_config, [run_args], self.rank, run_id, 1).execute()
                run_id += 1

        end = datetime.datetime.now()
        print(f'node {self.rank} GenerateWcetPerTaskSimulationsTask done {end - start}')

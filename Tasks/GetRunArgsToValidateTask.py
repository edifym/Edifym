import itertools
import datetime

import MainConfig
from Tasks.ITask import ITask
from typing import List, Iterator

from BenchmarkConfig import Task


class GetRunArgsToValidateTask(ITask):
    main_config: MainConfig
    tasks: List[List[Task]]
    rank: int

    def __init__(self, main_config: MainConfig, tasks: List[List[Task]], rank: int):
        self.main_config = main_config
        self.tasks = tasks
        self.rank = rank

    def run_args_for_task(self, task: Task, values: List[int]) -> str:
        args = ""

        total_values_expected = len(task.values)

        if len(values) != total_values_expected:
            print(f'Total values {len(values)} not equal to {total_values_expected}')
            raise Exception

        if len(task.values) == 0:
            args += "0"
        else:
            for val in values:
                args += f'{val};'
            args = args[:-1]

        return args

    def get_workloads(self, task: Task) -> Iterator[str]:
        for values in itertools.product(*[x.values for x in task.values]):
            yield self.run_args_for_task(task, values)

    def get_run_args(self, tasks: List[Task], run_args: str) -> Iterator[str]:
        if len(tasks) == 1:
            for extra_run_args in self.get_workloads(tasks[0]):
                yield f'{run_args} {extra_run_args}'
        else:
            for extra_run_args in self.get_workloads(tasks[0]):
                for ret in self.get_run_args(tasks[1:], f'{run_args} {extra_run_args}'):
                    yield ret

    def execute(self) -> Iterator[List[str]]:
        start = datetime.datetime.now()
        print(f'node {self.rank} starting GetRunArgsToValidateTask {len(self.tasks)} {start}')

        args_one = f"{self.main_config.executable} {len(self.tasks[0])} "
        args_two = f"{self.main_config.executable} {len(self.tasks[1])} "

        for task in self.tasks[0]:
            args_one += task.name + ";"

        for task in self.tasks[1]:
            args_two += task.name + ";"

        for run_args_one in self.get_run_args(self.tasks[0], args_one):
            for run_args_two in self.get_run_args(self.tasks[1], args_two):
                yield [run_args_one, run_args_two]

        end = datetime.datetime.now()
        print(f'node {self.rank} GetRunArgsToValidateTask done {end - start}')

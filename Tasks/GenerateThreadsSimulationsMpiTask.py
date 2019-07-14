import itertools
import datetime

import MainConfig
from Tasks.ITask import ITask
from typing import List, Iterator

from BenchmarkConfig import Benchmark, Task


def anydup(thelist):
    seen = set()
    for x in thelist:
        if x in seen: return True
        seen.add(x)
    return False


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

    def produce_task_permutations(self) -> Iterator[List[Task]]:
        print(f'node {self.rank} produce_task_permutations')
        for L in range(0, len(self.benchmark.tasks) + 1):
            count = 0
            print(f'L: {L}')
            for sub_benchmark in itertools.permutations(self.benchmark.tasks, L):
                if count > 10_000_000:
                    print(f'node {self.rank} breaking at {count}')
                    break

                count += 1

                yield sub_benchmark

    def produce_tasks_per_core_permutations(self, tasks: Iterator[List[Task]]) -> Iterator[List[List[Task]]]:
        for workloads in itertools.islice(itertools.permutations(tasks, self.main_config.num_cpus), self.rank * self.skip, (self.rank + 1) * self.skip):
            yield workloads

    def execute(self):
        start = datetime.datetime.now()
        print(f'node {self.rank} starting GenerateThreadsSimulationsTask {len(self.benchmark.tasks)} {start}')

        run_id = 1
        count_checked = 0
        tasks = self.produce_task_permutations()
        task_per_core = self.produce_tasks_per_core_permutations(tasks)
        runs_to_distribute = []
        for task_permutation in task_per_core:
            count_checked += 1

            if count_checked % 1_000_000 == 0:
                print(f'node {self.rank} checked {count_checked} tasks, added {run_id - 1} tasks')

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

            runs_to_distribute.append((run_args, run_id))
            run_id += 1

        end = datetime.datetime.now()
        print(f'node {self.rank} GenerateThreadsSimulationsTask done {end - start}')
        return runs_to_distribute

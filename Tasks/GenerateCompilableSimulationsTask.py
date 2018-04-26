from queue import Queue

import MainConfig
from BenchmarkConfig import Benchmark
import itertools

from Tasks.CompileSingleSimulationTask import CompileSingleSimulationTask
from Tasks.ITask import ITask
from typing import List


class GenerateCompilableSimulationsTask(ITask):
    main_config: MainConfig
    benchmark: Benchmark
    q: Queue

    def __init__(self, main_config: MainConfig, benchmark: Benchmark, q: Queue):
        self.main_config = main_config
        self.benchmark = benchmark
        self.q = q

    def produce_combinations(self) -> List[Benchmark]:
        combinations: List[Benchmark] = []

        # TODO generate empty subsets where compiled binary does nothing
        # TODO generate subset per core

        for L in range(1, len(self.benchmark.tasks) + 1):
            for sub_benchmark in itertools.combinations(self.benchmark.tasks, L):
                combinations.append(Benchmark(self.benchmark.name, sub_benchmark))

        return combinations

    def execute(self):
        combinations = self.produce_combinations()
        i = 1

        # TODO ensure that tasks with depends don't get scheduled before dependee has run.

        for sub_benchmark in combinations:
            new_task = CompileSingleSimulationTask(self.main_config, sub_benchmark, i)
            self.q.put(new_task)
            i += 1

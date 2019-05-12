import MainConfig
from BenchmarkConfig import Benchmark, Task
import itertools

from Tasks.CompileSingleSimulationTask import CompileSingleSimulationTask
from Tasks.ITask import ITask
from typing import Tuple, Iterator
from multiprocessing import Queue

class Benchmark2:
    name: str
    tasks: Tuple[Task]

    def __init__(self, name: str, tasks: Tuple[Task]):
        self.name = name
        self.tasks = tasks

    def __str__(self):
        return "Benchmark {%s, [%s]}" % (self.name, ', '.join(map(str, self.tasks)))

class GenerateCompilableSimulationsTask(ITask):
    main_config: MainConfig
    benchmark: Benchmark
    q: Queue

    def __init__(self, main_config: MainConfig, benchmark: Benchmark, q: Queue):
        self.main_config = main_config
        self.benchmark = benchmark
        self.q = q

    def produce_permutations(self) -> Iterator[Benchmark]:
        for L in range(0, len(self.benchmark.tasks) + 1):
            #print(L, self.benchmark.tasks, len(self.benchmark.tasks))
            for sub_benchmark in itertools.permutations(self.benchmark.tasks, L):
                #print(sub_benchmark)
                yield Benchmark(self.benchmark.name, list(sub_benchmark))

    def execute(self):
        print('Starting GenerateCompilableSimulationsTask')

        i = 1

        # TODO ensure that tasks with depends don't get scheduled before dependee has run.

        for sub_benchmark in self.produce_permutations():
            #print(f'going to compile {sub_benchmark}')
            new_task = CompileSingleSimulationTask(self.main_config, sub_benchmark, i)
            self.q.put(new_task)
            i += 1

        print(f'GenerateCompilableSimulationsTask done {i}')

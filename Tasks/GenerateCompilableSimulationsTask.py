import MainConfig
from BenchmarkConfig import Benchmark, Task
import itertools

from Tasks.CompileSingleSimulationTask import CompileSingleSimulationTask
from Tasks.ITask import ITask
from typing import Tuple, Iterator
from multiprocessing import Queue, Value


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
    shm_quit: Value

    def __init__(self, main_config: MainConfig, benchmark: Benchmark, q: Queue, shm_quit: Value):
        self.main_config = main_config
        self.benchmark = benchmark
        self.q = q
        self.shm_quit = shm_quit

    def produce_permutations(self) -> Iterator[Benchmark]:
        for sub_benchmark in itertools.permutations(self.benchmark.tasks, len(self.benchmark.tasks)):
            #print(sub_benchmark)
            yield Benchmark(self.benchmark.name, list(sub_benchmark))

    def execute(self):
        print('Starting GenerateCompilableSimulationsTask')

        i = 1

        # TODO ensure that tasks with depends don't get scheduled before dependee has run.

        for sub_benchmark in self.produce_permutations():
            #print(f'{i}: going to compile {sub_benchmark}')
            #new_task = CompileSingleSimulationTask(self.main_config, sub_benchmark, i)
            #self.q.put(new_task)
            i += 1
            if i % 1_000_000 == 0:
                print(f'{i}')
            if self.shm_quit.value:
                break

        print(f'GenerateCompilableSimulationsTask done {i}')

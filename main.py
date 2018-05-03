# execute gem5
# read input from config.json
# read input from benchmarks.json?
# Store output per run:
# - core/task configuration
# - input vars
# - ticks & time in seconds?
# -

import json
from queue import Empty

from MainConfig import MainConfig
from BenchmarkConfig import BenchmarkConfig
from Tasks.GenerateCompilableSimulationsTask import GenerateCompilableSimulationsTask
from Tasks.GenerateRunSimulationsTask import GenerateRunSimulationsTask
from multiprocessing import Pool, Process, Queue


def queue_worker(q):
    while True:
        task = q.get()
        task.execute()


if __name__ == "__main__":
    main_data = json.load(open('config.json'))
    benchmark_data = json.load(open('benchmarks.json'))
    main_config = MainConfig(main_data)
    benchmark_config = BenchmarkConfig(benchmark_data)
    q = Queue()
    GenerateCompilableSimulationsTask(main_config, benchmark_config.benchmarks[0], q).execute()

    # compiling single threaded

    while True:
        try:
            task = q.get_nowait()
            task.execute()
        except Empty:
            break

    GenerateRunSimulationsTask(main_config, q).execute()

    # run simulations multithreaded

    for i in range(0, 2):
        p = Process(target=queue_worker, args=(q,))
        p.start()

    queue_worker(q)

# execute gem5
# read input from config.json
# read input from benchmarks.json?
# Store output per run:
# - core/task configuration
# - input vars
# - ticks & time in seconds?
# -

import json
import signal
from queue import Queue, Empty

from MainConfig import MainConfig
from BenchmarkConfig import BenchmarkConfig
from Tasks.GenerateCompilableSimulationsTask import GenerateCompilableSimulationsTask
from Tasks.GenerateRunSimulationsTask import GenerateRunSimulationsTask
from multiprocessing import Pool

q = Queue()
should_quit = False


def queue_worker(x):
    while not should_quit:
        task = q.get()
        task.execute()
        q.task_done()


def signal_handler(signal, frame):
    should_quit = True


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    main_data = json.load(open('config.json'))
    benchmark_data = json.load(open('benchmarks.json'))
    main_config = MainConfig(main_data)
    benchmark_config = BenchmarkConfig(benchmark_data)
    GenerateCompilableSimulationsTask(main_config, benchmark_config.benchmarks[0], q).execute()

    # compiling single threaded

    while True:
        try:
            task = q.get_nowait()
            task.execute()
            q.task_done()
        except Empty:
            break

    GenerateRunSimulationsTask(main_config, q).execute()

    # run simulations multithreaded

    with Pool(4) as p:
        p.map(queue_worker, [1, 2, 3, 4])


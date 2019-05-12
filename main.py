# execute gem5
# read input from config.json
# read input from benchmarks.json?
# Store output per run:
# - core/task configuration
# - input vars
# - ticks & time in seconds?
# -

import json
import sys
from queue import Empty
import signal
from time import sleep

from MainConfig import MainConfig
from BenchmarkConfig import BenchmarkConfig
from Tasks.GenerateCompilableSimulationsTask import GenerateCompilableSimulationsTask
from Tasks.GenerateRunSimulationsTask import GenerateRunSimulationsTask
from multiprocessing import Process, Queue, Value

shm_quit = Value('b', False)


def signal_handler(sig, frame):
    print('Quitting all remaining workers')
    shm_quit.value = True


def queue_worker(q, id, local_shm_quit):
    print(f'starting worker {id}')

    while not local_shm_quit.value:
        try:
            task = q.get(False, 1000)
            task.execute()
        except Empty:
            print('No more tasks for worker {id}')
            break

    print(f'stopping worker {id} {local_shm_quit.value}')


if __name__ == "__main__":
    main_data = json.load(open('config.json'))
    benchmark_data = json.load(open('benchmarks.json'))
    main_config = MainConfig(main_data)
    benchmark_config = BenchmarkConfig(benchmark_data)
    q = Queue()

    signal.signal(signal.SIGINT, signal_handler)

    benchmark, = [bench for bench in benchmark_config.benchmarks if bench.name == main_config.benchmark]

    GenerateCompilableSimulationsTask(main_config, benchmark, q).execute()

    # compiling single threaded

    '''while not shm_quit.value:
        try:
            task = q.get(False, 1000)
            task.execute()
        except Empty:
            print('done compiling')
            break'''

    procs = []

    for i in range(0, main_config.num_workers - 1):
        p = Process(target=queue_worker, args=(q, i, shm_quit))
        p.start()
        procs.append(p)

    queue_worker(q, main_config.num_workers, shm_quit)

    if shm_quit.value:
        sleep(1)
        print('murdering self')
        for p in procs:
            p.terminate()
        sys.exit()

    #GenerateRunSimulationsTask(main_config, q).execute()

    # run simulations multithreaded

    '''for i in range(0, main_config.num_workers - 1):
        p = Process(target=queue_worker, args=(q, i))
        p.start()

    queue_worker(q, main_config.num_workers)'''

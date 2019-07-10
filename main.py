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

from MainConfig import MainConfig
from BenchmarkConfig import BenchmarkConfig
from Tasks.GenerateCompilableSimulationsTask import GenerateCompilableSimulationsTask
from Tasks.GenerateRunSimulationsTask import GenerateRunSimulationsTask
from multiprocessing import Process, Queue, Value

shm_quit = Value('b', False)


def signal_handler(sig, frame):
    print('Quitting all remaining workers')
    shm_quit.value = True


def queue_worker(queue: Queue, worker_id: int, local_shm_quit: Value):
    print(f'starting worker {worker_id}')

    while not local_shm_quit.value:
        try:
            task = queue.get(True, 0.5)
            task.execute()
        except Empty:
            print('No more tasks for worker {id}')
            break
        except:
            print(f'Unexpected exception {sys.exc_info()[0]}')
            break

    print(f'stopping worker {worker_id} {local_shm_quit.value}')


if __name__ == "__main__":
    main_data = json.load(open('config.json'))
    benchmark_data = json.load(open('benchmarks.json'))
    main_config = MainConfig(main_data)
    benchmark_config = BenchmarkConfig(benchmark_data)
    q = Queue()
    q.cancel_join_thread()

    signal.signal(signal.SIGINT, signal_handler)

    benchmark, = [bench for bench in benchmark_config.benchmarks if bench.name == main_config.benchmark]

    GenerateCompilableSimulationsTask(main_config, benchmark, q, shm_quit).execute()

    if shm_quit.value:
        sys.exit(1)

    for i in range(0, main_config.num_workers - 1):
        p = Process(target=queue_worker, args=(q, i, shm_quit))
        p.start()

    queue_worker(q, main_config.num_workers, shm_quit)

    if shm_quit.value:
        sys.exit(1)

    GenerateRunSimulationsTask(main_config, q, shm_quit).execute()

    if shm_quit.value:
        sys.exit(1)

    for i in range(0, main_config.num_workers - 1):
        p = Process(target=queue_worker, args=(q, i, shm_quit))
        p.start()

    queue_worker(q, main_config.num_workers, shm_quit)

import json
import sys
from queue import Empty
import signal

from MainConfig import MainConfig
from BenchmarkConfig import BenchmarkConfig
from Tasks.GenerateThreadsSimulationsTask import GenerateThreadsSimulationsTask
from multiprocessing import Process, Queue, Value
from time import sleep

shm_quit = Value('b', False)


def signal_handler(sig, frame):
    print('Quitting all remaining workers')
    global shm_quit
    shm_quit.value = True


def queue_worker(queue: Queue, worker_id: int):
    global shm_quit
    sleep(5)
    print('starting worker %s' % worker_id)

    while not shm_quit.value:
        try:
            task = queue.get(True, 0.5)
            task.execute()
        except Empty:
            print('No more tasks for worker %s', worker_id)
            break
        except:
            print('Unexpected exception %s' % sys.exc_info()[0])
            break

    print('stopping worker %s %s' % (worker_id, shm_quit.value))


if __name__ == "__main__":
    main_data = json.load(open('config.json'))
    benchmark_data = json.load(open('benchmarks.json'))
    main_config = MainConfig(main_data)
    benchmark_config = BenchmarkConfig(benchmark_data)
    q = Queue()
    q.cancel_join_thread()

    signal.signal(signal.SIGINT, signal_handler)

    benchmark, = [bench for bench in benchmark_config.benchmarks if bench.name == main_config.benchmark]

    for i in range(0, main_config.num_workers - 1):
        p = Process(target=queue_worker, args=(q, i))
        p.start()

    GenerateThreadsSimulationsTask(main_config, benchmark, q, shm_quit).execute()

    if shm_quit.value:
        sys.exit(1)

    queue_worker(q, main_config.num_workers)

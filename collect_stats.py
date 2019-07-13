# execute gem5
# read input from config.json
# read input from benchmarks.json?
# Store output per run:
# - core/task configuration
# - input vars
# - ticks & time in seconds?
# -

import json
import os
import signal
import sys
from queue import Empty

from MainConfig import MainConfig
from typing import List
from CommandHelper import CommandHelper
from multiprocessing import Process, Queue, Value

shm_quit = Value('b', False)


def signal_handler(sig, frame):
    print('Quitting')
    global shm_quit
    shm_quit.value = True


def queue_worker(dir_queue: Queue, totals_queue: Queue, worker_id: int):
    global shm_quit
    print(f'starting worker {worker_id}')

    while not shm_quit.value:
        try:
            run_dir = dir_queue.get(True, 0.5)
            #print(run_dir)
            CommandHelper.run_command(['mkdir', f'{run_dir}'], {}, main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}')
            CommandHelper.run_command(['zstd', '-d', '-f', f'{main_config.stats_dir}/{run_dir}/stats.txt.zst', '-o', 'stats.txt'], {}, main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}/{run_dir}')
            stats = CommandHelper.run_command_output(['awk', '/sim_sec/ {print $2}', f'stats.txt'], {}, f'{main_config.out_dir}/{run_dir}').splitlines()
            CommandHelper.run_command(['rm', '-rf', f'{run_dir}'], {}, main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}')

            totals_queue.put(stats[-1])
        except Empty:
            print(f'No more tasks for worker {id}')
            break
        except:
            print(f'Unexpected exception {sys.exc_info()[0]}')
            break

    print(f'stopping worker {worker_id} {shm_quit.value}')


def get_immediate_subdirectories(a_dir: str) -> List[str]:
    dirs = os.listdir(a_dir)
    subdirs = []

    for name in dirs:
        if os.path.isdir(os.path.join(a_dir, name)):
            subdirs.append(name)

    subdirs.sort()
    return subdirs


if __name__ == "__main__":
    main_data = json.load(open('config.json'))
    main_config = MainConfig(main_data)
    dir_q = Queue()
    dir_q.cancel_join_thread()

    totals_q = Queue()
    totals_q.cancel_join_thread()

    signal.signal(signal.SIGINT, signal_handler)
    print(main_config.stats_dir)

    totals = []
    runs = 0
    for run_dir in get_immediate_subdirectories(main_config.stats_dir):
        dir_q.put(run_dir)
        runs += 1

    for i in range(0, main_config.num_workers):
        p = Process(target=queue_worker, args=(dir_q, totals_q, i))
        p.start()

    while len(totals) < runs:
        try:
            totals.append(totals_q.get(True, 0.5))
            if len(totals) % 1000 == 0:
                print(len(totals))
        except Empty:
            print('No more tasks for main')
            break
        except:
            print(f'Unexpected exception {sys.exc_info()[0]}')
            break

    vals_dict = {}
    for val in totals:
        if val in vals_dict:
            vals_dict[val] += 1
        else:
            vals_dict[val] = 1
    print(max(totals))
    print(min(totals))
    print(vals_dict)

    '''import matplotlib.pylab as plt

    lists = [(x[5:], y) for x, y in sorted(vals_dict.items())] # sorted by key, return a list of tuples

    x, y = zip(*lists)  # unpack a list of pairs into two tuples

    plt.plot(x, y)
    plt.show()'''

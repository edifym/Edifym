import json
import os
import sys
import time
import distutils

from datetime import timedelta, datetime
from mpi4py import MPI

from MainConfig import MainConfig
from typing import List
from CommandHelper import CommandHelper


def get_immediate_subdirectories(a_dir: str, max_timestamp: float) -> List[str]:
    dirs = os.listdir(a_dir)
    subdirs = []

    for name in dirs:
        path = os.path.join(a_dir, name)
        if os.path.isdir(path) and os.path.getctime(path) < max_timestamp:
            subdirs.append(name)

    return subdirs


if __name__ == "__main__":
    main_data = json.load(open('config.json'))
    main_config = MainConfig(main_data)

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    totals = []
    runs = 0

    one = os.path.isdir(main_config.out_dir)
    print(f'node {rank} {main_config.out_dir} exists {one}')

    if not one:
        try:
            os.makedirs(main_config.out_dir, exist_ok=True)
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
            print(sys.exc_info()[0])

    if rank == 0:
        first_timestamp = os.path.getctime(f'{main_config.stats_dir}/run_0_1')
        max_timestamp = time.mktime((datetime.fromtimestamp(first_timestamp) + timedelta(minutes=5)).timetuple())
        data = get_immediate_subdirectories(main_config.stats_dir, max_timestamp)
        print(f'master data size {len(data)}')
        # dividing data into chunks
        chunks = [[] for _ in range(size)]
        for i, chunk in enumerate(data):
            chunks[i % size].append(chunk)
    else:
        time.sleep(0.05 * rank)
        distutils.file_util.copy_file(f'{main_config.stats_dir}/zstd-dict', f'{main_config.out_dir}/zstd-dict', update=1)
        data = None
        chunks = None

    data = comm.scatter(chunks, root=0)

    totals = []
    for run_dir in data:
        try:
            CommandHelper.run_command(['mkdir', '-p', f'{main_config.out_dir}/{run_dir}'], main_config.show_command_output, main_config.show_command_error)
            CommandHelper.run_command([main_config.zstd, '-D', f'{main_config.out_dir}/zstd-dict', '-d', '-f', f'{main_config.stats_dir}/{run_dir}/stats.txt.zst', '-o', 'stats.txt'], main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}/{run_dir}')
            stats = CommandHelper.run_command_output(['awk', '/sim_sec/ {print $2}', f'stats.txt'], f'{main_config.out_dir}/{run_dir}').splitlines()
            CommandHelper.run_command(['rm', '-rf', f'{run_dir}'], main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}')
            if len(stats) != 27:
                print(f'node {rank} run_dir {run_dir} incorrect stats length {len(stats)} {stats}')
            else:
                total_time_for_tasks = 0
                prev_time = 0
                for i in range(26):
                    if i % 2 == 0:
                        prev_time = int(stats[i][2:])
                    else:
                        #print(f'node {rank} adding {int(stats[i][2:]):,} {int(stats[i-1][2:]):,}')
                        total_time_for_tasks += int(stats[i][2:]) - int(stats[i-1][2:])
                #print(f'node {rank} adding total {total_time_for_tasks}')
                totals.append(total_time_for_tasks)
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
            print(sys.exc_info()[0])

    print(f'node {rank} gather')
    newData = comm.gather(totals, root=0)

    if rank == 0:
        import pickle
        flat_list = [item for sublist in newData for item in sublist]
        print(f'Node {rank} total results {len(flat_list)}')

        vals_dict = {}
        for val in flat_list:
            if val in vals_dict:
                vals_dict[val] += 1
            else:
                vals_dict[val] = 1
        print(max(flat_list))
        print(min(flat_list))
        print(vals_dict)

        f = open(f'{main_config.stats_dir}/dict.pkl', 'wb')
        pickle.dump(vals_dict, f)
        f.close()
    else:
        print(f'node {rank} done')

    '''import matplotlib.pylab as plt

    lists = [(x[5:], y) for x, y in sorted(vals_dict.items())] # sorted by key, return a list of tuples

    x, y = zip(*lists)  # unpack a list of pairs into two tuples

    plt.plot(x, y)
    plt.show()'''

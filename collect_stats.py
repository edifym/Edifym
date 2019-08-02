import json
import os
import sys
import time
import distutils.file_util

from datetime import timedelta, datetime
from mpi4py import MPI

from MainConfig import MainConfig
from typing import List
from CommandHelper import CommandHelper
from JsonHelper import JsonHelper


def get_immediate_subdirectories(a_dir: str, max_timestamp: float) -> List[str]:
    dirs = os.listdir(a_dir)
    subdirs = []

    for name in dirs:
        if name == "zstd-dict" or name == "dict.pkl":
            continue
        path = os.path.join(a_dir, name)
        if os.path.isdir(path) and os.path.getmtime(path) < max_timestamp:
            subdirs.append(name)

    return subdirs


if __name__ == "__main__":
    start = datetime.now()
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

    total_dirs = 0
    if rank == 0:
        first_timestamp = os.path.getmtime(f'{main_config.stats_dir}/run_0_1')
        max_timestamp = time.mktime((datetime.fromtimestamp(first_timestamp) + timedelta(minutes=120)).timetuple())
        data = get_immediate_subdirectories(main_config.stats_dir, max_timestamp)
        total_dirs = len(data)
        print(f'master data size {total_dirs}')
        # dividing data into chunks
        chunks = [[] for _ in range(size)]
        for i, chunk in enumerate(data):
            chunks[i % size].append(chunk)
    else:
        time.sleep(0.1 * rank)
        distutils.file_util.copy_file(f'{main_config.stats_dir}/zstd-dict', f'{main_config.out_dir}/zstd-dict', update=1)
        data = None
        chunks = None

    data = comm.scatter(chunks, root=0)

    totals = []
    total_zero = 0
    total_twentysix = 0
    total_other = 0
    highest_runtime = 0
    highest_dir = ""
    for run_dir in data:
        try:
            stats = JsonHelper.read_stats_from_workloads(f'{main_config.stats_dir}/{run_dir}/workloads.json')

            if stats[1] == 0:
                total_zero += 1
                print(f'node {rank} run_dir {run_dir} incorrect stats length {stats[1]} {stats}')
            elif stats[1] == 14:
                total_twentysix += 1
            elif stats[1] != 15:
                total_other += 1
                print(f'node {rank} run_dir {run_dir} incorrect stats length {stats[1]} {stats}')
            else:
                totals.append(stats[0])

                if stats[0] > highest_runtime:
                    highest_runtime = stats[0]
                    highest_dir = run_dir
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
            print(sys.exc_info()[0])

    print(f'node {rank} gather')
    newData = comm.gather((totals, total_zero, total_twentysix, total_other), root=0)

    if rank == 0:
        import pickle
        flat_list = [item for sublist in newData for item in sublist[0]]
        total_zero = sum([sublist[1] for sublist in newData])
        total_twentysix = sum([sublist[2] for sublist in newData])
        total_other = sum([sublist[3] for sublist in newData])
        print(f'Node {rank} total dirs {total_dirs} total results {len(flat_list)} zero_stats {total_zero} twentysix_stats(now 14) {total_twentysix} other_stats {total_other}')

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

        end = datetime.now()
        print(f'node {rank} done {end - start} - highest run_dir {highest_dir}')
    else:
        print(f'node {rank} done - highest run_dir {highest_dir}')

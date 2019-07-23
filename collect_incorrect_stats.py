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


def get_immediate_subdirectories(a_dir: str, max_timestamp: float) -> List[str]:
    dirs = os.listdir(a_dir)
    subdirs = []

    for name in dirs:
        if name == "zstd-dict" or name == "dict.pkl":
            continue
        path = os.path.join(a_dir, name)
        stats_file = os.path.join(path, 'stats.txt.zst')
        ctime = os.path.getmtime(stats_file)
        if os.path.isdir(path) and ctime < max_timestamp:
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

    if rank == 0:
        first_timestamp = os.path.getmtime(f'{main_config.stats_dir}/run_0_1')
        max_timestamp = time.mktime((datetime.fromtimestamp(first_timestamp) + timedelta(minutes=15)).timetuple())
        data = get_immediate_subdirectories(main_config.stats_dir, max_timestamp)
        print(f'master data size {len(data)}')
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

    total_zero = 0
    total_twentysix = 0
    total_other = 0
    for run_dir in data:
        try:
            CommandHelper.run_command(['mkdir', '-p', f'{main_config.out_dir}/{run_dir}'], main_config.show_command_output, main_config.show_command_error)
            CommandHelper.run_command(['zstd', '-D', f'{main_config.out_dir}/zstd-dict', '-d', '-f', f'{main_config.stats_dir}/{run_dir}/stats.txt.zst', '-o', 'stats.txt'], main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}/{run_dir}')
            stats = CommandHelper.run_command_output(['awk', '/sim_sec/ {print $2}', f'stats.txt'], f'{main_config.out_dir}/{run_dir}').splitlines()
            CommandHelper.run_command(['rm', '-rf', f'{run_dir}'], main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}')

            if len(stats) != 27:
                print(f'node {rank} run_dir {run_dir} incorrect stats length {len(stats)} {stats}')

            if len(stats) == 0:
                total_zero += 1
            elif len(stats) == 26:
                total_twentysix += 1
            elif len(stats) != 27:
                total_other += 1
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
            print(sys.exc_info()[0])

    print(f'node {rank} gather')
    newData = comm.gather((total_zero, total_twentysix, total_other), root=0)

    if rank == 0:
        total_zero = 0
        total_twentysix = 0
        total_other = 0

        for results in newData:
            total_zero += results[0]
            total_twentysix += results[1]
            total_other += results[2]

        print(f'Node {rank} results {total_zero} {total_twentysix} {total_other} {total_zero + total_twentysix + total_other}')

        end = datetime.now()
        print(f'node {rank} done {end - start}')
    else:
        print(f'node {rank} done')

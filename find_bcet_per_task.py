import json
import os
import sys
from mpi4py import MPI

from MainConfig import MainConfig
from typing import List
from CommandHelper import CommandHelper


def get_immediate_subdirectories(a_dir: str) -> List[str]:
    dirs = os.listdir(a_dir)
    subdirs = []

    for name in dirs:
        if name == "zstd-dict" or name == "dict.pkl":
            continue
        if os.path.isdir(os.path.join(a_dir, name)):
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
        dirs = get_immediate_subdirectories(main_config.stats_dir)
        runs = {}
        for dir in dirs:
            split_dir = dir.split('_')
            if split_dir[1] in runs:
                runs[split_dir[1]].append(dir)
            else:
                runs[split_dir[1]] = [dir]

        print(f'master data size {len(runs)} {runs}')
        # dividing data into chunks
        chunks = [[] for _ in range(size)]
        for i, chunk in enumerate(runs):
            print(f'i, chunk {i} {chunk} {runs[chunk]}')
            chunks[i % size].extend(runs[chunk])
    else:
        data = None
        chunks = None

    data = comm.scatter(chunks, root=0)
    print(f'Node {rank} data {len(data)}')

    totals = []
    for run_dir in data:
        try:
            CommandHelper.run_command(['mkdir', '-p', f'{main_config.out_dir}/{run_dir}'], main_config.show_command_output, main_config.show_command_error)
            CommandHelper.run_command([main_config.zstd, '-D', f'{main_config.stats_dir}/zstd-dict', '-d', '-f', f'{main_config.stats_dir}/{run_dir}/stats.txt.zst', '-o', 'stats.txt'], main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}/{run_dir}')
            stats = CommandHelper.run_command_output(['awk', '/sim_insts/ {print $2}', f'stats.txt'], f'{main_config.out_dir}/{run_dir}').splitlines()
            CommandHelper.run_command(['rm', '-rf', f'{run_dir}'], main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}')

            if len(stats) != 3:
                print(f'Expected three stat results, got {len(stats)} {stats}')
                raise Exception

            totals.append((run_dir, int(stats[1])))
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
            print(sys.exc_info()[0])

    if len(data) > 0:
        highest = 9999999999999999
        highest_run_dirs = []
        for run_dir, insts in totals:
            if insts == highest:
                highest = insts
                highest_run_dirs.append(run_dir)
            elif insts < highest:
                highest = insts
                highest_run_dirs = [run_dir]

        workload = CommandHelper.run_command_output(['cat', f'workloads.json'], f'{main_config.stats_dir}/{highest_run_dirs[0]}').splitlines()
        print(f'node {rank} highest workload {highest} {highest_run_dirs} {workload[1]}')

    print(f'node {rank} done')

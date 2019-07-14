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
        data = get_immediate_subdirectories(main_config.stats_dir)
        print(f'master data size {len(data)}')
        # dividing data into chunks
        chunks = [[] for _ in range(size)]
        for i, chunk in enumerate(data):
            chunks[i % size].append(chunk)
    else:
        data = None
        chunks = None

    data = comm.scatter(chunks, root=0)

    totals = []
    for run_dir in data:
        try:
            CommandHelper.run_command(['mkdir', '-p', f'{main_config.out_dir}/{run_dir}'], {}, main_config.show_command_output, main_config.show_command_error)
            CommandHelper.run_command([main_config.zstd, '-d', '-f', f'{main_config.stats_dir}/{run_dir}/stats.txt.zst', '-o', 'stats.txt'], {}, main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}/{run_dir}')
            stats = CommandHelper.run_command_output(['awk', '/sim_sec/ {print $2}', f'stats.txt'], {}, f'{main_config.out_dir}/{run_dir}').splitlines()
            CommandHelper.run_command(['rm', '-rf', f'{run_dir}'], {}, main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}')
            totals.append(stats[-1])
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
            print(sys.exc_info()[0])

    print(f'node {rank} gather')
    newData = comm.gather(totals, root=0)

    if rank == 0:
        flat_list = [item for sublist in newData for item in sublist]

        vals_dict = {}
        for val in flat_list:
            if val in vals_dict:
                vals_dict[val] += 1
            else:
                vals_dict[val] = 1
        print(max(flat_list))
        print(min(flat_list))
        print(vals_dict)
    else:
        print(f'node {rank} done')

    '''import matplotlib.pylab as plt

    lists = [(x[5:], y) for x, y in sorted(vals_dict.items())] # sorted by key, return a list of tuples

    x, y = zip(*lists)  # unpack a list of pairs into two tuples

    plt.plot(x, y)
    plt.show()'''

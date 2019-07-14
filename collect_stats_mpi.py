import json
import os
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
        CommandHelper.run_command(['mkdir', f'{run_dir}'], {}, main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}')
        CommandHelper.run_command([main_config.zstd, '-d', '-f', f'{main_config.stats_dir}/{run_dir}/stats.txt.zst', '-o', 'stats.txt'], {}, main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}/{run_dir}')
        stats = CommandHelper.run_command_output(['awk', '/sim_sec/ {print $2}', f'stats.txt'], {}, f'{main_config.out_dir}/{run_dir}').splitlines()
        CommandHelper.run_command(['rm', '-rf', f'{run_dir}'], {}, main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}')
        totals.append(stats[-1])

    newData = comm.gather(totals, root=0)

    if rank == 0:
        flat_list = [item for sublist in newData for item in sublist]
        print(f'master: {flat_list}')

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

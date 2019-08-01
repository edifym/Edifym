import json
import os
import sys
import time
import distutils.file_util

from datetime import datetime
from mpi4py import MPI

from MainConfig import MainConfig
from CommandHelper import CommandHelper


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
        data = CommandHelper.get_immediate_subdirectories(main_config.stats_dir)
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

    find_runs_with_this_time = 624
    identified_runs = []
    for run_dir in data:
        try:
            CommandHelper.run_command(['mkdir', '-p', f'{main_config.out_dir}/{run_dir}'], main_config.show_command_output, main_config.show_command_error)
            CommandHelper.run_command(['zstd', '-D', f'{main_config.out_dir}/zstd-dict', '-d', '-f', f'{main_config.stats_dir}/{run_dir}/stats.txt.zst', '-o', 'stats.txt'], main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}/{run_dir}')
            stats = CommandHelper.run_command_output(['awk', '/sim_sec/ {print $2}', f'stats.txt'], f'{main_config.out_dir}/{run_dir}').splitlines()
            CommandHelper.run_command(['rm', '-rf', f'{run_dir}'], main_config.show_command_output, main_config.show_command_error, f'{main_config.out_dir}')
            if len(stats) != 27:
                continue
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
                if total_time_for_tasks == find_runs_with_this_time:
                    totals.append(run_dir)
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
            print(sys.exc_info()[0])

    print(f'node {rank} gather')
    newData = comm.gather(totals, root=0)

    if rank == 0:
        flat_list = [item for sublist in newData for item in sublist]
        print(f'Node {rank} total dirs {total_dirs} total results {len(flat_list)}')
        print(f'Node {rank} list {flat_list}')
        end = datetime.now()
        print(f'node {rank} done {end - start}')
    else:
        print(f'node {rank} done')

import json
import sys
import os
import datetime
from mpi4py import MPI

from MainConfig import MainConfig
from BenchmarkConfig import BenchmarkConfig
from Tasks.GenerateWcetPerTaskSimulationsTask import GenerateWcetPerTaskSimulationsTask


if __name__ == "__main__":
    main_data = json.load(open('config.json'))
    benchmark_data = json.load(open('benchmarks.json'))
    main_config = MainConfig(main_data)
    benchmark_config = BenchmarkConfig(benchmark_data)

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

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

    benchmark, = [bench for bench in benchmark_config.benchmarks if bench.name == main_config.benchmark]

    start = datetime.datetime.now()

    if rank == 0:
        data = benchmark.tasks
        print(f'master data size {len(data)}')
        # dividing data into chunks
        chunks = [[] for _ in range(size)]
        for i, chunk in enumerate(data):
            chunks[i % size].append(chunk)
    else:
        data = None
        chunks = None

    data = comm.scatter(chunks, root=0)

    print(f'Node {rank} {len(data)} {data}')

    total_values = 0

    for task in data:
        task_values = 1
        for value in task.values:
            task_values *= len(value.values)
        total_values += task_values

    total_size = total_values

    print(f'Node {rank} total_size {total_size:,} total_values {total_values:,}')

    GenerateWcetPerTaskSimulationsTask(main_config, data, rank).execute()

    end = datetime.datetime.now()
    print(f'node {rank} done {end - start}')

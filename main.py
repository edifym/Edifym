import json
import sys
import os
import datetime
import math
from mpi4py import MPI

from MainConfig import MainConfig
from BenchmarkConfig import BenchmarkConfig
from Tasks.GenerateThreadsSimulationsTask import GenerateThreadsSimulationsTask
#from Tasks.GenerateThreadsAndValueSimulationsTask import GenerateThreadsAndValuesSimulationsTask


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

    total_permutations = math.factorial(len(benchmark.tasks))
    total_values = 1

    for task in benchmark.tasks:
        for value in task.values:
            total_values *= len(value.values)

    total_size = total_permutations*(len(benchmark.tasks) + 1)*total_values

    skip = int(total_permutations/size)
    print(f'total_size {total_size:,} total_permutations {total_permutations:,} total_values {total_values:,} skip {skip:,}')

    GenerateThreadsSimulationsTask(main_config, benchmark, rank, skip).execute()

    end = datetime.datetime.now()
    print(f'node {rank} done {end - start}')

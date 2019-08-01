import json
import sys
import os
from mpi4py import MPI
from typing import List

from MainConfig import MainConfig
from BenchmarkConfig import BenchmarkConfig, Task
from Tasks.ValidateSingleSimulationTask import ValidateSingleSimulationTask
from Tasks.GetRunArgsToValidateTask import GetRunArgsToValidateTask


def get_sorted_list(tasks: List[Task], task_names: List[str]) -> List[Task]:
    sorted_tasks = []

    for name in task_names:
        task, = [task for task in tasks if task.name == name]
        sorted_tasks.append(task)

    return sorted_tasks


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

    run_id = 0
    if rank == 0:
        tasks_one = get_sorted_list(benchmark.tasks, ["navigation_task", "link_fbw_send"])
        tasks_two = get_sorted_list(benchmark.tasks, ["test_ppm_task", "servo_transmit"])
        run_iter = iter(GetRunArgsToValidateTask(main_config, [tasks_one, tasks_two], rank).execute())

        # dividing data into chunks
        chunks = [[] for _ in range(size)]
        i = 0
        while True:
            if i % size == 0:
                i += 1
                if i > 1:
                    print(f'sending {i} {chunks}')
                    data = comm.scatter(chunks, root=0)
                    chunks = [[] for _ in range(size)]
            chunks[i % size].append(next(run_iter))
            i += 1
    else:
        while True:
            chunks = None
            run_args_chunk = comm.scatter(chunks, root=0)

            for run_args in run_args_chunk:
                ValidateSingleSimulationTask(main_config, [run_args[0], run_args[1]], rank, run_id, 2, 624).execute()
                run_id += 1


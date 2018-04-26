# execute gem5
# read input from config.json
# read input from benchmarks.json?
# Store output per run:
# - core/task configuration
# - input vars
# - ticks & time in seconds?
# -

import json
from queue import Queue

from MainConfig import MainConfig
from BenchmarkConfig import BenchmarkConfig
from Tasks.GenerateCompilableSimulationsTask import GenerateCompilableSimulationsTask
from Tasks.RunSingleSimulationTask import RunSingleSimulationTask

if __name__ == "__main__":
    main_data = json.load(open('config.json'))
    benchmark_data = json.load(open('benchmarks.json'))
    main_config = MainConfig(main_data)
    benchmark_config = BenchmarkConfig(benchmark_data)
    q = Queue()
    GenerateCompilableSimulationsTask(main_config, benchmark_config.benchmarks[0], q).execute()
    q.put(RunSingleSimulationTask(main_config, 1))
    while True:
        task = q.get()
        task.execute()
        q.task_done()

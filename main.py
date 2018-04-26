# execute gem5
# read input from config.json
# read input from benchmarks.json?
# Store output per run:
# - core/task configuration
# - input vars
# - ticks & time in seconds?
# -

import json

from MainConfig import MainConfig
from BenchmarkConfig import BenchmarkConfig
from Tasks.CompileSingleSimulationTask import CompileSingleSimulationITask

if __name__ == "__main__":
    main_data = json.load(open('config.json'))
    benchmark_data = json.load(open('benchmarks.json'))
    main_config = MainConfig(main_data)
    benchmark_config = BenchmarkConfig(benchmark_data)
    task = CompileSingleSimulationITask(main_config, benchmark_config.benchmarks[0])
    task.execute()
